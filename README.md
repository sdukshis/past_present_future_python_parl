## Benchmark environment

Apple MacBook M1 Pro 2021, 6 high performance + 2 efficient cores, 16GB RAM, macOS 12.0.1
## Benchmark results

### Python 3.13.0b1
.....................
count_primes_single: Mean +- std dev: 743 ms +- 10 ms
.....................
count_primes_multithreading: Mean +- std dev: 742 ms +- 7 ms
.....................
count_primes_interpreters: Mean +- std dev: 266 ms +- 7 ms
.....................
count_primes_multiprocessing: Mean +- std dev: 262 ms +- 9 ms

### Python 3.14.0a0 with GIL
.....................
count_primes_single: Mean +- std dev: 716 ms +- 24 ms
.....................
count_primes_multithreading: Mean +- std dev: 718 ms +- 13 ms
.....................
count_primes_interpreters: Mean +- std dev: 257 ms +- 5 ms
.....................
count_primes_multiprocessing: Mean +- std dev: 258 ms +- 13 ms

### Python 3.14.0a0 without GIL
count_primes_single: Mean +- std dev: 891 ms +- 24 ms
.....................
WARNING: the benchmark result may be unstable
* the standard deviation (65.0 ms) is 21% of the mean (306 ms)

Try to rerun the benchmark with more runs, values and/or loops.
Run 'python -m pyperf system tune' command to reduce the system jitter.
Use pyperf stats, pyperf dump and pyperf hist to analyze results.
Use --quiet option to hide these warnings.

count_primes_multithreading: Mean +- std dev: 306 ms +- 65 ms
.....................
count_primes_interpreters: Mean +- std dev: 391 ms +- 9 ms
.....................
count_primes_multiprocessing: Mean +- std dev: 315 ms +- 12 ms