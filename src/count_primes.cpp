// Count number of prime numbers less then input parameter

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <future>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

bool is_prime(int n) {
    if (n <= 1) return false;
    for (int i = 2; i < n; i++) {
        if (n % i == 0) return false;
    }
    return true;
}

int count_primes_worker(int begin, int end, int step) {
    int result = 0;
    for (int i = begin; i < end; i += step) {
        result += is_prime(i);
    }
    return result;
}

int count_primes(int n, int n_threads) {
    if (n < 3) return 0;
    if (n_threads < 1) {
        throw std::invalid_argument("n_threads must be positive number");
    }

    std::vector<std::future<int>> tasks;
    for (int i = 0; i < n_threads; ++i) {
        tasks.emplace_back(
            std::async(std::launch::async, count_primes_worker, 2*i + 1, n, 2*n_threads));
    }
    return std::transform_reduce(tasks.begin(), tasks.end(), 1, std::plus<int>{},
                                  [](auto &result) { return result.get(); });
}

extern "C" {
static PyObject *count_primes_py(PyObject *self, PyObject *args) {
    int n, n_threads;
    if (!PyArg_ParseTuple(args, "ii", &n, &n_threads)) {
        return nullptr;
    }
    return PyLong_FromLong(count_primes(n, n_threads));
}

static PyMethodDef module_methods[] = {
    {"count_primes", count_primes_py, METH_VARARGS, "Count number of prime numbers less then input parameter"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "count_primes",
    "Count number of prime numbers less then input parameter",
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit_count_primes(void) {
    return PyModule_Create(&module);
}
} // extern "C"

// int main(int argc, char *argv[]) {
//     using namespace std;
//     if (argc < 2) {
//         cout << "Usage: " << argv[0] << " n [nthreads]\n";
//         return EXIT_FAILURE;
//     }
//     int n = stoi(argv[1]);
//     if (n <= 0) {
//         cerr << "n must be positive number\n";
//         return EXIT_FAILURE;
//     }
//     int n_threads = (argc > 2) ? stoi(argv[2]) : std::thread::hardware_concurrency();
//     if (n_threads <= 0) {
//         cerr << "nthreads must be positive number\n";
//         return EXIT_FAILURE;
//     }

//     chrono::time_point start = chrono::high_resolution_clock::now();
//     int nprimes = count_primes(n, n_threads);
//     chrono::time_point end = chrono::high_resolution_clock::now();
//     chrono::duration<double> elapsed = end - start;
//     cout << nprimes << '\n';
//     cout << "It tooks " << elapsed.count() << " seconds with " << n_threads
//          << " threads\n";
//     return EXIT_SUCCESS;
// }
