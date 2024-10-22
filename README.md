# prime-number-calculator

## Index
- [Purpose](#purpose)
- [Development stack](#development-stack)
- [Local testing](#local-testing)
- [Environment for testing](#environment-for-testing)
    - [Running parallel code in the same machine](#running-parallel-code-in-the-same-machine)
    - [Running parallel code in multiple machines](#running-parallel-code-in-multiple-machines)
    - [Running sequential code](#running-sequential-code)
- [Performance tests](#performance-tests)
    - [Speedup](#speedup)
    - [Throughput](#throughput)
    - [Communication overhead](#communication-overhead)
    - [Full report](#full-report)
- [Performance tests using light parallel mode](#performance-tests-using-light-parallel-mode)
- [What is next](#what-is-next)

## Purpose
Given an initial number, the main purpose of this automation is to calculate the quantity of prime numbers in this range.

Example: Given the number 10, the algorithm will return that there are 4 prime numbers until 10.

You can run this algorithm:
- ... in sequential mode
- ... in paralell mode

For parallel mode we are using the farm pattern, which is compose by an emitter, a collector and one or more workers. The emitter organize the work and send tasks to the workers (distributing the tasks evenly). Then, the worker performs the actual work and send the result to collector. Finally, the collector merges this data and presents it to the user.

![](.docs/img/.pattern.drawio.png)

The main idea of this architecture is to scale the number of workers to achieve more speed. The more workers we have, the higher the performance (in theory). We'll see more about this in the [performance test](#performance-tests).

## Development stack
- Python: 3.11
- Libraries:
    - [mpi4py](https://pypi.org/project/mpi4py/)
    - [click](https://pypi.org/project/click/)
- Dev libraries:
    - [pytest](https://pypi.org/project/pytest/)
    - [coverage](https://pypi.org/project/coverage/)
    - [flake8](https://pypi.org/project/flake8/)

## Local testing

I'm using [pipenv](https://pipenv.pypa.io/en/latest/) to create and manage Python virtual environments. It helps us to isolate the libraries and differents Python versions.

To initialize the virtual environment just run:
```sh
pipenv install -d
pipenv shell
```

To run code using __sequential mode__:
```sh
python app.py --mode sequential --until-number 1000
```

> Where 1000 represents the max number to search for prime numbers.

It's important to comment that to run this code in parallel mode I'm using [OpenMPI](https://www.open-mpi.org/). In case you are using Windows in your development environment, even if you run this code in sequential mode, you must [install Microsoft MPI](https://learn.microsoft.com/en-us/message-passing-interface/microsoft-mpi). If you don't, a common error that may happen is:
```
ImportError: DLL load failed while importing MPI: Não foi possível encontrar o módulo especificado.
```


## Environment for testing

To run this code in a testing environment, we first need to create this environment following [these steps](./.docs/ENVIRONMENT.md).

The next steps, you must run just on __primary__.

You must access the shared folder and clone this repository:
```sh
cd /home/mpihpc/shared
git clone https://github.com/gabrielrih/setrem-parallel-programming.git
```

Then you can finally run the code inside the repo:
```sh
cd setrem-parallel-programming
```

### Running parallel code in the same machine

Running the code in the same machine:
```sh
mpirun -np 3 python app.py --mode parallel --until-number 10000
```

> Note that in this case the _mpirun_ are running the code in three different processes but all of them in the same machine. Another important thing is that each process is created in a differente vCore, so, in this case, the VM must have three or more vCores.


### Running parallel code in multiple machines

Running the code in multiple machines:
```sh
mpirun -np 3 --machinefile /home/mpihpc/.cluster_hostfile python app.py --mode parallel --until-number 10000
```

> Note that in this case the _mpirun_ are running using three different processes. By default, each process are allocated in a different vCore. If the -np value is bigger than the number of vCores in all the cluster, the default behavior is generate an error.

### Running sequential code

Running the sequential code. It uses just a single vCore.
```sh
python app.py --mode sequential --until-number 10000
```

## Performance tests

I ran performance tests using the sequential and the parallel mode. All the tests were performed on the __primary__ node in the testing environment previously created (5 vCores and 1GB RAM).

In theory, if the process took 10 seconds to run in sequential mode, if you have two processes it would take half of that, which is 5 seconds; if you have three processes it would take one third of that, 3.3 seconds; and so one and so far. But, in real world it's not posible for many reasons. One of them is that not all of your code is parallel, there would always be some parts that will continue runinng sequentially. Other reasons could be hardware limitation, memory usage, networking and more.

### Speedup
When you run a code sequentially, using a single vCore, it would take an amount of time to finishs. When you run your code in parallel, using two or more vCores, it would probably takes a different amount of time. The division by this two times will generates the speedup ([click here for more details](https://en.wikipedia.org/wiki/Amdahl%27s_law)).

$$ S = {T(1) \over T(N)} $$

> Where T(1) is the amount of time it takes to run sequentially and T(N) is the amount of time is takes to run in parallel (N is the number of vCores used).

The speedup graphic is normally presents by vCores, however, using the farm pattern, two of the vCores are used by emitter and collector and it does not have parallel code. This way, it makes more sense to generate the graphic by the number os workers and not the total of vCores used. In a simple example, if it's using four vCores, just two of them would be workers (parallel code).

The tests were divided into three categories and the same test in each category was ran five times.
- The first category was to generate prime numbers until 30,000.
- The second, until 50,000.
- And the last one, until 100,000.

Then, I calculate the average time it took in each category and them I calculated the speedup in each category using this average time.

The final speedup was the average of speedups in all categories.

![](.docs/img/speedup_graphic.png)

As you can see in the graphic above, when I used just a single worker, in fact the speedup is less than one. It means, using a single worker the code is slower than running it in sequential mode. In fact, it was surprising for me, because I thought the division of work between emitter, collector and worker, would be enough to improve the performance. The reason of that probably is the comunication overhead and the complex code.

However, from two workers the performance is improved by 24%. And using three workers the performance gets even better, 55%. This is really interesting because we are increasing the number of workers and the performance increases more and more. It would be also interesting to calculate the limitation of this approach, which means, what is the maximum of workers I can have where performance still increases? Note that probably in a certain number of workers the performance would stabilize, so this is the maximum scalability you can have. More than that you would probably have to improve the code or scale horizontally.

### Throughput

Another interesting metric is throughput. 

$$ T = {tasks \over time(seconds)} $$

> The number os tasks in this case is how many numbers it can check if it's prime or not.

The logic to check if a number is prime or not gets slower as the number gets bigger. For example, checking if then number 1,000 is prime is much faster than checking if 100,000 is prime. You can clearly see it in the table below.

| Workers | Until number | Speedup (avg) | Throughput (avg) | Time it took (avg) |
| :-----: | :----------: | :-----------: | :--------------: | :----------------: |
| 2       | 30,000       | 1.2           | 7,141            | 4.3 seconds        |
| 2       | 50,000       | 1.2           | 4,282            | 11.8 seconds       |
| 2       | 100,000      | 1.5           | 2,524            | 39.8 seconds       |

Note that although the speedup increased as the input number gets bigger, the throughput drastically reduced. It indicates that if you input a really big number, the algorithm "will continue running almost forever", getting slower and slower.

However, comparing the throughput average when using more workers, the throughput increased.

![](.docs/img/throughput.png)

Probably there would be a limit, just like speedup, but I couldn't check it here because of hardware limitation.

### Communication overhead
It's also important to comment about communication overhead. The OpenMPI protocol has to establish communication between processes (emitter, collector and workers) and obviously there is a cost to do that. The first version of the code, I was sending the data from emitter to worker one by one. Using this strategy the parallel code was 30% slower than sequential mode even using three workers (5 vCores in total). To solve this, I changed this logic to send data in batches of 50 instead of sending one by one. It decreased the communication overhead in 50 times and then the parallel code finally took some advantage comparing to the sequential one.

See [paralle.py file](./src/prime/parallel.py) for more details.

## Performance tests using light parallel mode
The tests ran above was performed sending all the results from the worker to the collector. However, for the purpose of this code, the collector need to know just the prime numbers. That way, I could simplify the logic to send data from worker to collector just when the number is prime. It reduced drastically the number of exchange messages between worker and collector. For example, if until_number is 100,000, in the normal parallel mode, there would be 100,000 messages sent from worker to collector. In the light parallel mode, just 9,592 messages would be sent to the collector.

To use this light parallel mode, instead of run _--mode parallel_, just use _--mode light_parallel_.

```sh
mpirun -np 3 python app.py --mode light_parallel --until-number 10000
```

The performance result in this second approach is much better than the previous one. Remember that in the previous one, the speedup for just one worker was less than one, so even using three vCores, the parallel code was slower than the sequential one. Also remember that the maximum of improvement we had was 55% (using three workers).

Now, using the light parallel mode, even using a single worker, the performance improvement was 28% (see the graphic below).

![](.docs/img/speedup_graphic_for_light_mode.png)

And then, using two workers, the performance improved 129% (which is amazing). However, it's interesting to note that using three workers the speedup was almost the same that using just two workers. It's important because it shows that probably we would have better performance adding more workers than two or three.

You can see this same behavior in the throughput graphic:

![](.docs/img/throughput_for_light_mode.png)

### Full report
To access the full test report, you can look at [performance_tests.xlsx](./.docs/performance_test.xlsx).

## What is next
To finish, there are some aproaches and changes I could try in the future to improve the performance of the parallel code even more:
- __Change the batch size__: I ran tests just using the batch value of 50. But, if I try changing this values, maybe the performance would be even better.
- __Horizontal scaling__: The performance test was ran just in a single machine. It's a good idea to test it in a cluster of nodes. Maybe, using higher numbers the performance would be better.

