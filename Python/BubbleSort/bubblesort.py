def bubblesort(container = []):
    """
        Bubble sort with first optimization.

        Parameters
        ----------
        container : a Python mutable list of values
                    which has implemented __len__, __getitem__ and __setitem__.

        Returns
        -------
        container : Sorted container

        Examples
        ----------
        >>> bubblesort([7,1,2,6,4,2,3])
        [1, 2, 2, 3, 4, 6, 7]

        >>> bubblesort(['a', 'c', 'b'])
        ['a', 'b', 'c']
    """

    # setting up variables
    length = len(container)
    changed = True

    while changed:
        changed = False
        for i in range(length - 1):
            if container[i] > container[i + 1]:
                container[i], container[i + 1] = container[i + 1], container[i]
                changed = True
        length -= 1
    return container