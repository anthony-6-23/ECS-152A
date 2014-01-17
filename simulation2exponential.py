import simpy
import random
import math

env = simpy.Environment()


done = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
time_slot = 0       #The time slot we are currently in
sent_packets = [0, 0, 0, 0, 0, 0, 0,0, 0]    #If sent_packets is 1, it is ok to send.
                  #If it is 0, no packet is sent. If > 1, collision 
successful = [0,0,0,0,0,0,0,0, 0]
time_to_send_all = 0
lambda_list = [.01, .02, .03, .04, .05, .06, .07, .08, .09]

#############
#Defining the packet class
#############

class Source(object):
    def __init__(self, env, node_number, lambdax):
        self.buffer_count = [0]
        self.env = env
        track = buffer_tracker(self.buffer_count, node_number, lambdax)
        self.proc = env.process(self.generate(self.buffer_count, node_number, lambdax))

    
    def generate(self, buffer_count, node_number, lambdax):
        
        global time_to_send_all
        global time_slot

        for x in range(1, 100):
            arrivalTime = random.expovariate(lambdax)
            packet = Packet(env, arrivalTime, x, buffer_count, node_number)
            yield env.timeout(arrivalTime)
        done[int(lambdax*100 -1)] = done[int(lambdax*100 - 1)] + 1
        
        if done[int(lambdax*100 - 1)] == 10:
                time_to_send_all = time_slot 
                throughput = 1.0* successful[int(lambdax*100 - 1)]/time_to_send_all
                print('The throughput for lambda = %f is %f' 
                        %(lambdax, throughput))

class buffer_tracker(object):
    def __init__(self, buffer_count, node_number, lambdax):
        self.proc = env.process(self.call(buffer_count, node_number, lambdax))
    
    def call(self, buffer_count, node_number, lambdax):

        global sent_packets
        number_of_collisions = 0
        slot_to_send = 1

        yield env.timeout(.01)
        while True:
        
            yield env.timeout(.99)
            #print('Time for node %d is %f' %(node_number, env.now))
            #Send only if you have something to send 
            #and if it is your slot to send
            
            
            if (time_slot == slot_to_send):
                
                if(buffer_count[0] > 0): #If buffer has something to send

                    sent_packets[int(lambdax * 100 -1)]  = sent_packets[int(lambdax*100 -1)]+1
                    #print('Sent packets is %d' %(sent_packets))
                    yield env.timeout(.01)
                    if sent_packets[int(lambdax * 100 -1)] == 1:
                        buffer_count[0] -= 1
                        number_of_collisions = 0    #Reset number of collisions to 0
                        slot_to_send = slot_to_send + 1
                        successful[int(lambdax*100 - 1)] = successful[int(lambdax*100 - 1)] + 1
                        #print('Packet at node %d is leaving at time %f' %(node_number, env.now))
                    else: #There is a collision
                        
                        number_of_collisions += 1
                        #Binary backoff algorithm
                        k = min(number_of_collisions, 10)
                        upper = math.pow(2, k)
                        slot_to_send = random.randint(1, upper) + slot_to_send
                        #print('Sent packets is %d' %(sent_packets))

                        #print('Collision at node %d. Slot to send is now %d \n'
                                #%(node_number, slot_to_send))
                        
                else:   #We have nothing to 
                    yield env.timeout(.01)
                    slot_to_send += 1
            else:
                yield env.timeout(.01)
            

    

class Packet(object):
    def __init__(self, env, time, pkt_number, buffer_count, node_number):
        self.env = env
        self.proc = env.process(self.run(time, pkt_number, buffer_count, node_number))

    def run(self, time, pkt_number, buffer_count, node_number):
        
        global sent_packets

        #Time for a packet to arrive
   
        yield env.timeout(time)
        #print('Packet %d  at node %d is arriving at time %f' %(pkt_number, node_number, env.now))
       
        #Waiting in buffer to be serviced

        buffer_count[0] = buffer_count[0] + 1
        


#The class ethernet manages the time slots and watches for collisions
class Ethernet(object):
    def __init__(self, env):
        self.env = env
        self.proc = env.process(self.track_time(env))

    def track_time(self, env):
        global time_slot
        global sent_packets
        global time_to_send_all
       
        global index

        while True:
            
            yield env.timeout(1)
            time_slot = time_slot + 1
            sent_packets[0] = 0
            sent_packets[1] = 0
            sent_packets[2] = 0
            sent_packets[3] = 0
            sent_packets[4] = 0
            sent_packets[5] = 0
            sent_packets[6] = 0
            sent_packets[7] = 0
            sent_packets[8] = 0

                
##############


ethernet = Ethernet(env)

index = 0
def spread(env, lambdax):
    for x in range(1, 11):   #How many nodes
        
 
        Source(env, x, lambdax)

def Start(env):
    
    global index
    while index < 9:
        #print ('Lambda: %f'  %lambda_list[index])
        spread(env, lambda_list[index])
        index = index + 1

start = Start(env)        
env.run(until = 400000)
