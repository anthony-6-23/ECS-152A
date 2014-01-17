
import simpy
import random


env = simpy.Environment()
service = simpy.Resource(env, capacity = 1)
buffer_count = 0
buffer_size = 10
dropped_packets = 0
total_packets = 10000
lambda_list = [0.2, 0.4, 0.6, 0.8, 0.9, 0.99]
#############
#Defining the packet class
#############

class Source(object):
    def __init__(self, env, service):
        self.env = env
        self.proc = env.process(self.generate(service))
   
    def generate(self, service):
        index = 0
        global buffer_size 
        global dropped_packets
        buffer_size = 10
        print ('Buffer Size is %d' %(buffer_size))
        while index < 6 :
                for x in range(1, total_packets):
			        arrivalTime = random.expovariate(lambda_list[index])
			        packet = Packet(env, arrivalTime, x, service)
			        yield env.timeout(arrivalTime)
                print ('Lambda: %f : Packet Loss Probability: %f'  %(lambda_list[index],dropped_packets *1.0/total_packets))
                dropped_packets = 0
                index = index + 1
        index = 0
        buffer_size = 50
        print ('Buffer Size is %d' %(buffer_size))
        while index < 6 :
                for x in range(1, total_packets):
                        arrivalTime = random.expovariate(lambda_list[index])
                        packet = Packet(env, arrivalTime, x, service)
                        yield env.timeout(arrivalTime)
                print ('Lambda: %f : Packet Loss Probability: %f'  %(lambda_list[index],dropped_packets *1.0/total_packets))
                dropped_packets = 0
                index = index + 1

class Packet(object):
 	def __init__(self, env, time, pkt_number, service):
		self.env = env
		self.proc = env.process(self.run(time, pkt_number, service))

	def run(self, time, pkt_number, service):
		
		global buffer_size
		global dropped_packets
		global buffer_count

		#Time for a packet to arrive
		yield env.timeout(time)		
		#print('Packet %d arriving at time %f' %(pkt_number, env.now))

		#Waiting in buffer to be serviced
		#If buffer is full, the packet is dropped
		
		if buffer_size == buffer_count:
			dropped_packets = dropped_packets + 1			
		#	print('Packet %d was dropped' %pkt_number)
		#	print('The number of dropped packets is %d ' %dropped_packets)
		
		else:	#Else the packet is put into the queue
			buffer_count = buffer_count + 1
		#	print ('Packet %d is in buffer at position %d' %(pkt_number, buffer_count))
			
			#Now waiting in buffer
			with service.request() as req:
				yield req
				#Now packet is serviced
				buffer_count = buffer_count - 1
		#		print('Packet %d started be serviced at %f' %(pkt_number, env.now))
				yield env.process(self.watching())
				
		#	print('Packet %d is leaving at time %f' %(pkt_number, env.now))
		

	def watching(self):
		serviceTime = random.expovariate(1.0)
		yield self.env.timeout(serviceTime)
		
##############
s = Source(env, service)
env.run(until = 1000000)
