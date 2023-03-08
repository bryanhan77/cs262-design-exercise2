<!-- "While working on this, keep a lab notebook in which you note the design decisions you have made. Then, run the scale model at least 5 times for at least one minute each time. Examine the logs, and discuss (in the lab book) the size of the jumps in the values for the logical clocks, drift in the values of the local logical clocks in the different machines (you can get a god’s eye view because of the system time), and the impact different timings on such things as gaps in the logical clock values and length of the message queue. Observations and reflections about the model and the results of running the model are more than welcome.

Once you have run this on three virtual machines that can vary their internal times by an order of magnitude, try running it with a smaller variation in the clock cycles and a smaller probability of the event being internal. What differences do those variations make? Add these observations to your lab notebook. Play around, and see if you can find something interesting." -->

# Lab Notebook

## Design Decisions

3/3/2023 Sat
- Today we started working on the clock-model. We first attended Varun's section and had a general idea of what we wanted our model to look like and how it should achieve each of the design specs. First, it is a peer-to-peer model with three machine processes happening concurrently. I first thought that the model should be similar to the client-server model we implemented for design exericse 1, but after communicating this idea to Varun, he said it's not the right idea and pointed me to a peer-to-peer model that only needed three bi-directional connections between the three machines. After some thought, we realized that it is much cleaner this way, and it's more distributed, which means there's no need for a contralized server to monitor every process. 

- We used the source code that Varun provided, and soon realized that although it allows us to connect three processes with each other, they are far from ideal in achieving what the specs had required us do. The first thing we changed was moving the producer thread from its own separate thread back to the main machine thread for each of the processes. This was because a process doesn't constantly produce messages to send to other machine processes. A process is always listening for incoming messages, so the consumer can be on its own thread but only sends a message if there are no messages within its msg_queue. Furthermore, it rolls a number from 1 to 3 using a random number generator that generates from range 1 to 10. Therefore, we moved the producer process from its own thread to the main machine thread in a while loop format.

- Then, I set the clockrate of each machine. By this point, I realized that there need to be a way of passing process information (config, clockrate, socket pointers, msg_queue messages, etc.) between different threads within the same process. We could've used global variables or pass dictionaries between functions, but there are lots of information to be passed and everything must be fed to the machine function to be used in the main while loop, so we decided the best way to approach this is by creating a new class called MachineProcess, and for each machine process, we instantiated an instance of this class in order to store all the information that we need between different threads and functions. After implementing it this way, the code looked much cleaner and well-organized.

- We implemented the logical clock based on what was described in the reading and lecture notes. The logical clock updates for every atomic operation of send, receive, or internal event. 

- For number of clock cycles per second, we made a for loop inside the while loop to perform atomic actions clockrate number of times, and we time the total execution time for performing these actions. Then, after every iteration of clockrate number of cycles, we wait (1 - cyclesExecutionTime) before entering next iteration of the while loop. We chose to do the clockrate this way because we wanted to check every second what is printed out, and pausing between each second for almost a second allows us to check for correctness of the operations with ease. 

<!-- Then, run the scale model at least 5 times for at least one minute each time. 

Examine the logs, and discuss (in the lab book) the size of the jumps in the values for the logical clocks, drift in the values of the local logical clocks in the different machines (you can get a god’s eye view because of the system time)

and the impact different timings on such things as gaps in the logical clock values and length of the message queue. Observations and reflections about the model and the results of running the model are more than welcome.

Once you have run this on three virtual machines that can vary their internal times by an order of magnitude, try running it with a smaller variation in the clock cycles and a smaller probability of the event being internal. What differences do those variations make? Add these observations to your lab notebook. Play around, and see if you can find something interesting." -->

## Data & Discussion of Experiements

### Setup
3/6 Mon: 
- Process 1 is served on port 18001, and it produces on port 28001. 
- Process 2 is served on port 28001, and it produces on port 38001. 
- Process 3 is served on port 38001, and it produces on port 18001. 

This is a very simple feedback loop to model our machine processes. Each peer-to-peer connection is bi-directional. 

### Running the scale model: 
### Trial 1

Process 1 - Server port: 18001, Client port: 28001. Clockrate: 6. 

Process 2 - Server port: 28001, Client port: 38001. Clockrate: 1. 

Process 3 - Server port: 38001, Client port: 18001. Clockrate: 4. 

**Observations:**

*Size of the jumps in logical clocks:*
- For Process 1, the logical clock incremented by 1 almost perfectly each time for 385 times. The biggest jump was 2, and it only happened once from 48 to 50. 
- For Process 2, the logical clock incremented in chunks almost all the time. The biggest jump size was 13 (from 26 to 39). 
- For Process 3, the logical clock incremented by 1 most of the time, but sometimes jumped in chuncks ranging from 2 to 10 (from clock 16 to 26). 

*Drift in the values of logical clocks in different machines:*
- Process 1's operation count is 384.
- Process 2's operation count is 64. 
- Process 3's operation count is 256. 
- Process 1 ended with logical clock = 385 by time 2023-03-07 14:21:55.258262. 
- Process 2 ended with logical clock = 245 by time 2023-03-07 14:21:55.260005. 
- Process 3 ended with logical clock = 387 by time 2023-03-07 14:21:55.260190.  

*Impact different timings have on gaps in the logical clock values, length of the message queue, and other observations:*
- Higher the clockrate, more up-to-date the logical clock value is. 
- Length of the message queue for process 1 (clockrate 6) and process 3 (clockrate 4) are 0 for most of the time, but for process 2 (with clockrate 1), the speed of processing the message couldn't keep up with the length that the message queue is growing at, so the length of the message queue kept increasing. By the end of the 64 seconds, the length of Process 2's message queue has grown to 26. 
- Because process 2 couldn't keep up with processing the messages, it only received messages throughput the process, and only sent a message to another machine process at the very beginning of the trial. 


### Trial 2

Process 1 - Server port: 18001, Client port: 28001. Clockrate: 4.  

Process 2 - Server port: 28001, Client port: 38001. Clockrate: 2. 

Process 3 - Server port: 38001, Client port: 18001. Clockrate: 1. 

**Observations:** 
*Size of the jumps in logical clocks:*
- For Process 1, the logical clock incremented perfectly by 1 each time for 272 times (48 seconds, clockrate = 4). 
- For Process 2, the logical clock incremented sometimes by 1 and sometimes in chunks. The biggest jump size was 14 (jumping from 12 to 26). 
- For Process 3, the logical clock incremented mostly in chunks, with the biggest jump size being 18 (from 154 to 172). 

*Drift in the values of logical clocks in different machines:* 
- Process 1's operation count is 272. 
- Process 2's operation count is 136. 
- Process 3's operation count is 68.  
- Process 1 ended with logical clock = 272 by time 2023-03-07 14:41:36.337288. 
- Process 2 ended with logical clock = 267 by time 2023-03-07 14:41:36.337241. 
- Process 3 ended with logical clock = 264 by time 2023-03-07 14:41:36.337234. 
- The higher the clockrate, the more accurate the logical clock would be for representing the current state, and the less drift from actual clock time it has. The lower the clockrate, the greater the drift away from the true logical clock time a process has. 

*Impact different timings have on gaps in the logical clock values, length of the message queue, and other observations:* 
- For process 1 (clockrate 4), the queue length is 0 for most of the time. For process 2 (clockrate 2), the queue length is 0 for most of the time, but the times that it is 1 is more. For Process 3 (clockrate 1), the queue length is 0 for half of the time, and other times it ranges from 1 to 5. 


### Trial 3

Process 1 - Server port: 18001, Client port: 28001. Clockrate: 4.

Process 2 - Server port: 28001, Client port: 38001. Clockrate: 1. 

Process 3 - Server port: 38001, Client port: 18001. Clockrate: 1. 

**Observations:** 
*Size of the jumps in logical clocks:* 
- For Process 1, the logical clock incremented perfectly by 1 each time for 252 times (in 63 seconds). 
- For Process 2, the logical clock incremented in chunks for most of the time, and the largest jump size was 20 (from 135 to 155). 
- For Process 3, the logical clock incremented in chunks for most of the time, and the largest jump size was 19 (from 84 to 103). 

*Drift in the values of logical clocks in different machines:* 
- Process 1's operation count is 252.
- Process 2's operation count is 63. 
- Process 3's operation count is 63. 
- Process 1 ended with logical clock = 252 by time 2023-03-07 15:24:13.313319. 
- Process 2 ended with logical clock = 63 by time 2023-03-07 15:24:13.282573. 
- Process 3 ended with logical clock = 63 by time 2023-03-07 15:24:13.284712. 

*Impact different timings have on gaps in the logical clock values, length of the message queue:* 
- The length of queue is 0 for process 1 (clockrate 4) all the way through, and the length of the queue for process 2 and 3 (clockrate 1) are more than 0 some of the times. Interesting enough, process 3's queue length increased insteadily toward the second half to a maximum size of 5, and the same didn't happen for process 2, although both process 2 and 3 have the same clockrate. 
- The slower the process is at processing incoming messages (if it has a slow clockrate), the less message it will send to other processes and the increase to its logical clock will be coarse. 


*Other observations and reflections about the model and results:* 
- Process 3 (clockrate = 1) lags behind process 2 (clockrate = 6) in logical clock, and as a result, process 1 (clockrate = 5), being fed by process 3 which lags behind in logical clock, is also lagging behind in logical clock despite having a high clockrate of 5. Process 3 is lagging behind because it has yet to process the messages from Process 2 stored in its queue. Process 1 lags behind in its clockrate because process 3 is busy processing its receives and haven't send a message to process 1 in ages (actually, it has never sent a message to process 1, so process 1's clockrate has been just its own incrementation this whole time). 


### Trial 4

Process 1 - Server port: 18001, Client port: 28001. Clockrate: 5. 

Process 2 - Server port: 28001, Client port: 38001. Clockrate: 5. 

Process 3 - Server port: 38001, Client port: 18001. Clockrate: 1. 

**Observations:** 
*Size of the jumps in logical clocks:* 
- For Process 1, the logical clock incremented mostly by 1 each time, and the largest jump was 4 (56 to 60). 
- For Process 2, the logical clock incremented mostly by 1 each time, and the largest jump was 3 (305 to 308). 
- For Process 3, the logical clock incremented in chunks for most of the time, and the largest jump was 11 (195 to 206). 

*Drift in the values of logical clocks in different machines:* 
- Process 1's operation count is 345. 
- Process 2's operation count is 345. 
- Process 3's operation count is 69.  
- Process 1 ended with logical clock = 361 by time 2023-03-07 15:53:45.645864. 
- Process 2 ended with logical clock = 363 by time 2023-03-07 15:53:45.646442. 
- Process 3 ended with logical clock = 212 by time 2023-03-07 15:53:45.646711. 

*Impact different timings have on gaps in the logical clock values, length of the message queue:*
- Length of the queue for process 3 increased steadily over the 69 second period. At the end, its queue length was 39. Queue is empty for both process 1 and 2 most of the time (clockrate 5 each). Logical clock values increased mostly in big chunks for process 3 because it always lags behind the processes with clockrate 5. The clockrate 5 processes are mostly similar throughout the period. 
- Logical clock is way behind for process 3, as it ended with 212 where the other processes all have processes above 360. 
- Logical clock is behind for process 3 because the later messages were stored in its queue -- it didn't have time to process all of the messages and update its logical clock to the latest. 


### Trial 5

Process 1 - Server port: 18001, Client port: 28001. Clockrate: 6. 

Process 2 - Server port: 28001, Client port: 38001. Clockrate: 4. 

Process 3 - Server port: 38001, Client port: 18001. Clockrate: 2. 

**Observations:** 
*Size of the jumps in logical clocks:* 
- For Process 1, the logical clock incremented mostly by 1 for most of the time, and the largest jump size was 2 (only happened once). 
- For Process 2, the logical clock incremented mostly by 1 each time, but occasionally it jumped by larger sizes. The largest jumping size was 17, from 77 to 94. 
- For Process 3, the logical clock incremented in chunks for most of the time, and the largest jump was 11 (195 to 206). 

*Drift in the values of logical clocks in different machines:* 
- Process 1's operation count is 438 
- Process 2's operation count is 292
- Process 3's operation count is 146.
- Process 1 ended with logical clock = 440 by time 2023-03-07 16:18:13.445606.  
- Process 2 ended with logical clock = 436 by time 2023-03-07 16:18:13.445599. 
- Process 3 ended with logical clock = 418 by time 2023-03-07 16:18:13.428510. 

*Impact different timings have on gaps in the logical clock values, length of the message queue:* 
- Message queue was empty for process 1 and 2 for most of the time, and process queue ranges from 1 to 11 for process 3 (clockrate 2) for most of the time. 
- The logical clock pattern for each of the processes are to be expected. The one with the most updated logical clock was the process with the greatest clockrate (process 1, clockrate 6), and the one with the middle clockrate (process 2, clockrate 4), and the one with the least clockrate had the logical clock with the most drift from the others (process 3, clockrate 2). 


<!-- Once you have run this on three virtual machines that can vary their internal times by an order of magnitude, try running it with a smaller variation in the clock cycles and a smaller probability of the event being internal. What differences do those variations make? Add these observations to your lab notebook. Play around, and see if you can find something interesting. -->


### Trial 6: Testing with logical clock

Process 1 - Server port: 18001, Client port: 28001. Clockrate: 4. 

Process 2 - Server port: 28001, Client port: 38001. Clockrate: 2.  

Process 3 - Server port: 38001, Client port: 18001. Clockrate: 5. 

Chance of internal event: changed from 7/10 to 2/5. 
Total runtime: 75 seconds. 

**Observations:** 
- Most things are similar, except for the fact that process 3, which has the highest clockrate, now has a higher level of drift where its logic clock is 11 more than its number of events (386 for logic clock, and 375 for number of events it had), despite having the highest clockrate among the three processes. 
- Process 2, which has a clockrate of 2, ended with a queue length of 47 -- the highest queue length recorded among the trials. This is definintely caused by decreased chance of internal events. Because internal events are less likelly to happen, sends are now more common. Because sends are more common, more messages are sent from processes with higher clockrates to processes with lower clockrates, and thus there are increases to the backlogging of messages, as observed by Process's 2's long message queue by the end of the 75 second runtime. 


### Trial 7: Testing with logical clock 

Process 1 - Server port: 18001, Client port: 28001. Clockrate: 1. 

Process 2 - Server port: 28001, Client port: 38001. Clockrate: 4.  

Process 3 - Server port: 38001, Client port: 18001. Clockrate: 2. 

Chance of internal event: changed from 7/10 to 2/5. 
Total runtime: 60 seconds. 

**Observations:** 
*Size of the jumps in logical clocks:* 
- For Process 1, the logical clock incremented in chunks, and the largest jump size was 8. 
- For Process 2, the logical clock increamented perfectly by 1 each time, for 240 times. 
- For Process 3, the logical clock incremented in chunks, and surprisingly it had an updated logical clock of 241 by the end. 

*Drift in the values of logical clocks in different machines:*
- Process 1's operation count is 60.
- Process 2's operation count is 240.
- Process 3's operation count is 120.
- Process 1 ended with logical clock = 127 by time 2023-03-07 19:22:12.231913. 
- Process 2 ended with logical clock = 240 by time 2023-03-07 19:22:12.230469. 
- Process 3 ended with logical clock = 241 by time 2023-03-07 19:22:12.231208.

*Observations:* 
- Interestingly, process 3 has a more updated logical clock than process 2, even though Process 3 only has a clockrate of 2 whereas process 2 has a clockrate of 4. 
- Similar observations to trial 6. For processes with slower clockrate (process 1), the length of the message queue increased at a much higher pace than it did when the internal event happened more frequently than it does now. 
- This means that the model probably will not scale when we add more machines, which means more sends AND more internal processes, and the message queue will just get longer and longer even for machines on high clockrates. 
- In a distributed system, it is important to consider the latency at which requests can be processed, and it's also important to consider load balancing, since a single machine may not be able to scale and handle the requests of the whole network, which is observed when we see the increase of message queue length when the number of sends increase and the number of internal processes decrease. It's important to incorporate a system where all machines can work together, and not let the low clockrate of one machine slow down the whole network system. This can be accomplished through efficient load balancing, upgrading the clockrate of slow machines, and adopting a network topology that enables bisection bandwidth so that messages can be processed swiftly and efficiently. A single machine's lack of latency can slow down the whole system, so as systems engineers, we must take the whole picture into consideration when designing such systems. 