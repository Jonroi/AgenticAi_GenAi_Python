def add_numbers():
    """
    This function calculates the sum of 10 and 10. It doesn't take any parameters,
    therefore it always returns the same value, 20.
    
    Parameters: None

    Return:
    int: This function always returns 20, which is the result of 10 + 10.

    Examples:
    >>> add_numbers()
    20

    Edge Cases:
    Since this function doesn't take any parameters and always calculates the same values, 
    there are no edge cases.

    """
    return 10 + 10

print(add_numbers())

import unittest

def add_numbers():
    """
    This function calculates the sum of 10 and 10. It doesn't take any parameters,
    therefore it always returns the same value, 20.
    
    Parameters: None

    Return:
    int: This function always returns 20, which is the result of 10 + 10.

    Examples:
    >>> add_numbers()
    20

    Edge Cases:
    Since this function doesn't take any parameters and always calculates the same values, 
    there are no edge cases.

    """
    return 10 + 10

class TestAddNumbers(unittest.TestCase):
    def test_add_numbers(self):
        self.assertEqual(add_numbers(), 20)
        
if __name__ == '__main__':
    unittest.main()