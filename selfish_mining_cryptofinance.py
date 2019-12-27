import numpy
import collections
import time
import random


"""
the class takes a dictionary as an input, this dictionary containes:    the number of block to be mined
                                                                        the hash power of the dishonest miner
                                                                        the probability that an honest miner mines on top of the dishonest chain

"""


class selfish_mining_sim:
    
    def __init__(self, **d):
        ##########################
        self.__number_of_blocks_to_mine=d['nb_blocks']
        self.__dishonet_hash_power=d['dishonest_hash']
        self.__mining_on_top_prob=d['mining_on_top']

        self.__advance=0 #at the start the honest and dishonest don't get to have a head start
        
        ########################### Counting of blocks #################
        self.__hidden_chain=0 #length of mined blocks in secret
        self.__public_chain=0 #length of the public chain
        self.__validated_by_honest=0 #the number that blocks the honest miner will have gained/published
        self.__validated_by_dishonest=0 #the number of the blocks that the dishonest mineers will have gained
        self.__count=1 #starting at 1 because ortherwise we would stop at 2015 blocks
       
        ########################## Difficulty adjustement ##############
        self.__expected_time= 10 #expected time to validate a block in minutes
        self.__number_of_blocks_before_adjustement=2016 #in bitcoin the number of blocks validated before difficulty adjustment is 2016
        self.__real_time=None #the time it took to mine the blocks.
        self.__correction_factor=1 #correction factor= real_time/(number_of_blocks_before_adjustement*expected_time)

        self.__Mined_Blocks=[] #total number of blocks mined
        self.__current_time=0
        self.__last_time_difficulty_changed=0 #allows to keep track of when the difficulty change happened

        ########################## Revenue and results ###################
        self.__revenue_ration=0 #revenue ration revenue/time
        self.__number_of_validated_block=0
        self.__orphan_block=0

        ########################## Read and write
        self.__display=True
        self.__write=True
            
    
    def simulation(self):
        """
        time to find a block 
        """
        separation_of_blocks_by_2016=[2016 for x in range(0, self.__number_of_blocks_to_mine//2016)]+[self.__number_of_blocks_to_mine%2016] #creates the number of difficumty adjustement to be made iun the sumulation runtime

        for i in range(0, len(separation_of_blocks_by_2016)): #we will loop the number of times there will be a change of difficulty
           # TimesBlocksFoundSM = map(lambda x: x+self.__currentTimestamp, list(np.cumsum(np.random.exponential(1/(self.__alpha)*10/self.__B, SepBlocksEach2016[i]))))
            time_for_each_block_found_by_dishonest=map(lambda x: x+self.__current_time, list(numpy.cumsum(numpy.random.exponential(1/(self.__dishonet_hash_power)*10/self.__correction_factor, separation_of_blocks_by_2016[i]))))
            time_for_each_block_found_by_honest=map(lambda x: x+self.__current_time, list(numpy.cumsum(numpy.random.exponential(1/(1-self.__dishonet_hash_power)*10/self.__correction_factor, separation_of_blocks_by_2016[i]))))

            ####################### putting them in a dictionary and merging the dictionaries
            
            time_for_each_block_found_by_dishonest={x: 'dishonest' for x in time_for_each_block_found_by_dishonest}
            time_for_each_block_found_by_honest={x: 'honest' for x in time_for_each_block_found_by_honest}
            Blocks_merge={**time_for_each_block_found_by_dishonest,**time_for_each_block_found_by_honest}
            Blocks_merge=collections.OrderedDict(sorted(Blocks_merge.items()))
            #this is the time when the 2016th has been discovered by each party

            Blocks_merge=list(Blocks_merge.items())
            Blocks_merge=[(a,b) for (a,b) in zip(Blocks_merge, range(0,separation_of_blocks_by_2016[i]*2))]

            for ((current_time, which),block_number) in Blocks_merge:
                if self.__count>self.__number_of_blocks_to_mine: #check if we have made more simulation thant needed
                    break
                self.__count+=1
                self.__current_time=current_time #we place ourselves at the 
                if which=='honest':
                    self.mined_by_honest() #found by the honest
                else:
                    self.mined_by_dishonest() #found by the dishonest
                
                ######################## write in file ########################
                if self.__write and self.__number_of_validated_block%200==0:
                    self.write()
                
                if self.__number_of_validated_block//((i+1)*2016)>0:
                    self.new_results(difficulty_adjustment=True) #if the the number of validated block is superior to 2016 the difficulty must be adjusted
                    break


        self.__advance=self.__hidden_chain-self.__public_chain #publishing the hidden chain if there is an advance
        if self.__advance>0:
            self.__validated_by_dishonest+=self.__hidden_chain
            self.__hidden_chain, self.__public_chain= 0,0 #reset the count in the chains
            self.new_results()
        #if self.__display:
           # print(self) 


    def mined_by_honest(self):
        self.__advance=self.__hidden_chain-self.__public_chain
        self.__public_chain+1
        if self.__advance==0:
            self.__validated_by_honest+=1 #the honest miners automaticaly validates their blocks as they publish them if theu are not behinf th edishonest miner
            rand=random.uniform(0,1) #this will be to know to which chain the blocks it appends to
            if self.__hidden_chain>0 and rand <= self.__mining_on_top_prob:
                self.__validated_by_dishonest+= 1
            elif self.__hidden_chain>0 and rand > self.__mining_on_top_prob:
                self.__validated_by_honest+=1
            self.__hidden_chain, self.__public_chain= 0,0 #reset the count in the chains


        elif self.__advance>=2:
            self.__validated_by_dishonest+=self.__hidden_chain #the dishonest miner publishes his blocks in order to bypass the honest miner
            self.__hidden_chain, self.__public_chain= 0,0 #reset the count in the chains

        self.new_results #actualises the results variables


    def mined_by_dishonest(self):
        self.__advance=self.__hidden_chain-self.__public_chain
        self.__hidden_chain+=1
        if self.__advance==0 and self.__hidden_chain==2:
            self.__hidden_chain, self.__public_chain= 0,0 #reset the count in the chains
            self.__validated_by_dishonest+=2
        self.new_results()

    
    def new_results(self, difficulty_adjustment=False):
        self.__number_of_validated_block=self.__validated_by_dishonest+self.__validated_by_honest #update the number of validated blocks
        self.__orphan_block=self.__number_of_blocks_to_mine-self.__number_of_validated_block #alculation of ditched blocks 
        if self.__validated_by_honest or self.__validated_by_dishonest:
            self.__revenue_ration=100*round(self.__validated_by_dishonest/(self.__number_of_validated_block), 3)
        if difficulty_adjustment:
            self.__real_time=self.__current_time-self.__last_time_difficulty_changed
            self.__correction_factor=self.__correction_factor*self.__real_time/(self.__expected_time*self.__number_of_blocks_before_adjustement)
            self.__last_time_difficulty_changed=self.__current_time

    def write(self):
        results=[self.__dishonet_hash_power,self.__mining_on_top_prob,self.__number_of_blocks_to_mine,self.__current_time,self.__number_of_validated_block,self.__validated_by_honest,self.__validated_by_dishonest,self.__count, self.__dishonet_hash_power*self.__current_time/10]
        if self.__real_time is not None:
            results.extend([self.__real_time, 20160*100/self.__real_time])
        else:
            results.extend(['/','/'])

        with open('results_cryptofinance.txt','a',encoding='utf-8') as file:
            file.write(','.join([str(x) for x in results])+'\n')




start = time.time()
hashpower = list(i/100 for i in range(1, 50, 1)) #range(1, 50, 1) | 50 => 0, 0.5, 0.01
probatomine = list(i/100 for i in range(1, 100, 5)) #range(1, 100, 1) | 100 => 0, 1, 0.01
count = 0 #pourcentage done
for alpha in hashpower:
    for gamma in probatomine:
        ## Before and after Difficulty Adjustment (whole time range)
        new = selfish_mining_sim(**{'nb_blocks':150000, 'dishonest_hash':alpha, 'mining_on_top':gamma, 'write':True})
        new.simulation()
    count += 1/len(hashpower)
    print("progress :" + str(round(count,2)*100) + "%\n")
duration = time.time()-start
print("Tooks " + str(round(duration,2)) + " seconds")

