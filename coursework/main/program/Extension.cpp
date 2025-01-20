#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <algorithm>

namespace py = pybind11;

int partition(std::vector<std::string>& logins, int low, int high) {
    std::string pivot = logins[high];
    int i = low - 1;

    for (int j = low; j < high; ++j) {
        if (logins[j] <= pivot) {
            i++;
            std::swap(logins[i], logins[j]);
        }
    }
    std::swap(logins[i + 1], logins[high]);
    return i + 1;
}

void quickSort(std::vector<std::string>& logins, int low, int high) {
    if (low < high) {
        int pi = partition(logins, low, high);
        quickSort(logins, low, pi - 1);
        quickSort(logins, pi + 1, high);
    }
}

int binarySearch(const std::vector<std::string>& logins, const std::string& target) {
    int left = 0, right = logins.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (logins[mid] == target) {
            return mid;
        } else if (logins[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1;
}

PYBIND11_MODULE(Extension, m) {
    m.def("binarySearch", &binarySearch, "Функція бінарного пошуку",
          py::arg("logins"), py::arg("target"));

    m.def("quickSort", &quickSort, "Функція швидкого сортування",
          py::arg("logins"), py::arg("low"), py::arg("high"));


}
