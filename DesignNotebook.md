"While working on this, keep a lab notebook in which you note the design decisions you have made. Then, run the scale model at least 5 times for at least one minute each time. Examine the logs, and discuss (in the lab book) the size of the jumps in the values for the logical clocks, drift in the values of the local logical clocks in the different machines (you can get a god’s eye view because of the system time), and the impact different timings on such things as gaps in the logical clock values and length of the message queue. Observations and reflections about the model and the results of running the model are more than welcome.

Once you have run this on three virtual machines that can vary their internal times by an order of magnitude, try running it with a smaller variation in the clock cycles and a smaller probability of the event being internal. What differences do those variations make? Add these observations to your lab notebook. Play around, and see if you can find something interesting."


3/3/2023 Sat
- Today we started working on the clock-model. We first attended Varun's section and had a general idea of what we wanted our model to look like and how it should achieve each of the design specs. First, it is a peer-to-peer model with three machine processes happening concurrently. I communicated with Varun with my idea on doing a client-server model like we did for design exercise 1, and he said it's not the right idea and pointed me to a peer-to-peer model that only needed three bi-directional connections between the three machines. It is way cleaner this way, as we have realized, and it's more distributed, no need for a contralized server to monitor every process. 
- We used the source code that Varun provided, and soon realized although it allows us to connect three processes with each other, they are far from ideal in achieving what the specs had required us do. The first thing we changed was moving the producer thread from its own separate thread back to the main machine thread for each of the processes. This is because a process doesn't constantly produce messages to send to other machine processes; a process is always listening for incoming messages, so the consumer can be on its own thread, but it only sends a message if there are no messages within its msg_queue, and further, when it rolls a number from 1 to 3 using a random number generator that generates from range 1 to 10. Therefore, we moved the producer process from its own thread to the main machine thread in a while loop format
- Then, I set the clockrate of each machine. By this point, I realized that there need to be a way of passing process information (config, clockrate, socket pointers, msg_queue messages, etc.) between different threads within the same process. We could've used global variables or pass dictionaries between functions, but there are lots of information to be passed and everything must be fed to the machine function to be used in the main while loop, so we decided the best way to approach this is by creating a new class called MachineProcess, and for each machine process, we instantiate an instance of this class in order to store all the information that we need between different threads and functions. This is exactly what we did. 
- We implemented the logical clock based on what was described in the reading and lecture notes. The logical clock updates for every atomic operation of send, receive, or internal event. 
- For number of clock cycles per second, we made a for loop inside the while loop to perform atomic actions clockrate number of times, and we time the total execution time for performing these actions. Then, after every iteration of clockrate number of cycles, we wait (1 - cyclesExecutionTime) before entering next iteration of the while loop. We chose to do the clockrate this way because we wanted to check every second what is printed out, and pausing between each second for almost a second allows us to check for correctness of the operations with ease. 



Then, run the scale model at least 5 times for at least one minute each time. 

Examine the logs, and discuss (in the lab book) the size of the jumps in the values for the logical clocks, drift in the values of the local logical clocks in the different machines (you can get a god’s eye view because of the system time)

and the impact different timings on such things as gaps in the logical clock values and length of the message queue. Observations and reflections about the model and the results of running the model are more than welcome.

Once you have run this on three virtual machines that can vary their internal times by an order of magnitude, try running it with a smaller variation in the clock cycles and a smaller probability of the event being internal. What differences do those variations make? Add these observations to your lab notebook. Play around, and see if you can find something interesting."


3/6 Mon: 
- Process 1 is served on port 18001, and it produces on port 28001. 
- Process 2 is served on port 28001, and it produces on port 38001. 
- Process 3 is served on port 38001, and it produces on port 18001. 
This is a very simple feedback loop to model our machine processes. 

Running the scale model: 


1. Trial 1
Process 1 - Server port: 18001, Client port: 28001. Clockrate: 4. 
Process 2 - Server port: 28001, Client port: 38001. Clockrate: 3. 
Process 3 - Server port: 38001, Client port: 18001. Clockrate: 2. 

Observations: 
size of the jumps in logical clocks: 
- For Process 1, the logical clock incremented by 1 perfectly each time for 252 times (63 seconds, since it has clockrate of 4). 
- For Process 2, the logical clock incremented by 1 most of the time, but sometimes has jumps of ranging from size 2 to 12. 
- For Process 3, the logical clock incremented sometimes by 1, other times by 2-5, and up to 22. 

drift in the values of logical clocks in different machines: 
- Process 1's operation count is 252.
- Process 2's operation count is 189. 
- Process 3's operation count is 126. 
- Process 1 ended with logical clock = 252 by time 2023-03-06 21:09:02.538756. 
- Process 2 ended with logical clock = 247 by time 2023-03-06 21:09:02.533818. 
- Process 3 ended with logical clock = 244 by time 2023-03-06 21:09:02.533807. 

impact different timings have on gaps in the logical clock values, length of the message queue. 
- Higher the clockrate, more up-to-date the logical clock value is. 
- Length of the message queue for All three processes is mostly 0, with occasional lengths of 2s and 1s scatter in between. 
Not enough data to tell; or, I think the clockrates are too similar among the three processes to witness significant differences in this trial. 


2. Trial 2
Process 1 - Server port: 18001, Client port: 28001. Clockrate: 3. 
Process 2 - Server port: 28001, Client port: 38001. Clockrate: 1. 
Process 3 - Server port: 38001, Client port: 18001. Clockrate: 5. 

Observations: 
size of the jumps in logical clocks: 
- For Process 1, the logical clock incremented mostly by 1 each time, but occasionlly jumped ranging from size 2-9. 
- For Process 2, the logical clock incremented mostly in chunks, with sizes ranging from 2-35.
- For Process 3, the logical clock incremented by 1 perfectly each time for 335 times (67 seconds, process 3 has clockrate = 5).

drift in the values of logical clocks in different machines: 
- Process 1's operation count is 201.
- Process 2's operation count is 67. 
- Process 3's operation count is 335. 
- Process 1 ended with logical clock = 330 by time 2023-03-06 21:29:55.066246. 
- Process 2 ended with logical clock = 327 by time 2023-03-06 21:29:55.072152. 
- Process 3 ended with logical clock = 335 by time 2023-03-06 21:29:55.070251. 

impact different timings have on gaps in the logical clock values, length of the message queue. 
- I'm beginning to realize that machines with the highest clockrate is almost always updated on the latest clockrate, and machines with less clockrate updates its logical clock value coarsely (in chunks) because it's always behind. 
- Most of the message queue size still remain 0 across all three machine processes, but we can clearly see that machine with clockrate 5 always have a queue size of zero, while machines with clockrate of 1 or 3 periodically have queue size of 2 or 1, with it being a smaller proportion of the times for machine with clockrate 3 than clockrate 1. 


3. Trial 3
Process 1 - Server port: 18001, Client port: 28001. Clockrate: 5. 
Process 2 - Server port: 28001, Client port: 38001. Clockrate: 6. 
Process 3 - Server port: 38001, Client port: 18001. Clockrate: 1. 

Observations: 
size of the jumps in logical clocks: 
- For Process 1, the logical clock incremented perfectly by 1 each time (for 345 times, 69 seconds, since process 1 has clockrate = 5). 
- For Process 2, the logical clock incremented perfectly by 1 each time (for 414 times, 69 seconds, since process 2 has clockrate = 6). 
- For Process 3, the logical clock incremented mostly in chunks, ranging from jumps of size 2 to 27. 

drift in the values of logical clocks in different machines: 
- Process 1's operation count is 345.
- Process 2's operation count is 414.
- Process 3's operation count is 69. 
- Process 1 ended with logical clock = 345 by time 2023-03-06 21:55:19.477522
- Process 2 ended with logical clock = 414 by time 2023-03-06 21:55:20.479208. 
- Process 3 ended with logical clock = 371 by time 2023-03-06 21:55:19.477024. 

impact different timings have on gaps in the logical clock values, length of the message queue. 
- I noticed that the machine with clockrate 1 does nothing but receive messages. It makes sense when I examine its message queue: the length of the message queue is almost always more than 0. 
- length of Process 2's message queue is 0 for most of the time, and occasionally 1. 
- Length of Process 1's message queue is 0 for all of the time. 

Other observations and reflections about the model and results: 
- Process 3 (clockrate = 1) lags behind process 2 (clockrate = 6) in logical clock, and as a result, process 1 (clockrate = 5), being fed by process 3 which lags behind in logical clock, is also lagging behind in logical clock despite having a high clockrate of 5. Process 3 is lagging behind because it has yet to process the messages from Process 2 stored in its queue. Process 1 lags behind in its clockrate because process 3 is busy processing its receives and haven't send a message to process 1 in ages (actually, it has never sent a message to process 1, so process 1's clockrate has been just its own incrementation this whole time). 


