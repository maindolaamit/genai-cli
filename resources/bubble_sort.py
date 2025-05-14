Several variations of bubble sort exist. Here are two Python functions demonstrating bubble sort:  one optimized, and one that's more straightforward but less efficient.


**Version 1: Optimized Bubble Sort**

This version includes a flag to check if any swaps were made in a pass. If no swaps are made, the list is already sorted, and the algorithm terminates early.  This significantly improves performance on nearly-sorted lists.

```python
def bubble_sort_optimized(list_):
    """Sorts a list using optimized bubble sort.

    Args:
        list_: The list to be sorted.

    Returns:
        The sorted list.
    """
    n = len(list_)
    for i in range(n):
        swapped = False  # Flag to optimize
        for j in range(0, n - i - 1):
            if list_[j] > list_[j + 1]:
                list_[j], list_[j + 1] = list_[j + 1], list_[j]
                swapped = True
        if not swapped:
            break  # Exit if no two elements were swapped in inner loop
    return list_

```

**Version 2: Basic Bubble Sort (Less Efficient)**

This version is simpler but performs unnecessary comparisons even if the list is already sorted.

```python
def bubble_sort_basic(list_):
    """Sorts a list using basic bubble sort (less efficient).

    Args:
        list_: The list to be sorted.

    Returns:
        The sorted list.
    """
    n = len(list_)
    for i in range(n):
        for j in range(0, n - i - 1):
            if list_[j] > list_[j + 1]:
                list_[j], list_[j + 1] = list_[j + 1], list_[j]
    return list_

```

**Example Usage:**

```python
my_list = [64, 34, 25, 12, 22, 11, 90]

sorted_list_optimized = bubble_sort_optimized(my_list.copy())  # Use copy to avoid modifying original
sorted_list_basic = bubble_sort_basic(my_list.copy())

print("Optimized Bubble Sort:", sorted_list_optimized)
print("Basic Bubble Sort:", sorted_list_basic)
```

Remember that Bubble Sort has a time complexity of O(n^2) in the worst and average cases, making it inefficient for large lists.  Consider using more efficient algorithms like merge sort or quicksort for larger datasets.  However, Bubble Sort's simplicity makes it useful for educational purposes or very small lists.
