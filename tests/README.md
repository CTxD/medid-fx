# Testing setup
- For each module to be tested, make a folder with the same name containig a `__init__.py`-file
- For each file in a module to be tested make a single test file following the naming convention `test_<name of file to be tested>.py`

- Inside the file, import the module to be tested as such:
    ```python
    import source.<name of module>.<name of file> as <shorthand name>
    ``` 

- Pytest automatically registers all tests following the above naming conventions and runs these.

## Example of structure:
```
├─ source
|   └─ myPackage
|       └─ __init__.py
|       └─ foo.py
|       └─ bar.py
| ...
├─ tests
|   └─ myPackage
|       └─ __init__.py
|       └─ test_foo.py
|       └─ test_bar.py
```

# Test conventions
For each functionality in a file to be tested, several tests should be written. Each test *must* start with `test_<functionality being tested>` and followed by a brief explanation of what is being tested.

Example tests for an arbitrary math module:
```python
import source.math.add as add

    def test_add_1_and_2(self):
        assert add(1, 2) == 3

    def test_add_neg1_and_2(self):
        assert add(-1, 2) == 1
``` 

Following the naming convention means tests are short and concise and only test a specific functionality. This means multiple test-methods must be written to test a single functionality. The naming convention allows for quick identification of what exactly is tested and if a test fails it allows for easy identification of *which* test has failed. See https://docs.python-guide.org/writing/tests/ for guidelines and good practices w.r.t. writing tests. (The link refers to unittesting, however a lot of the practices can be used for pytest aswell.) 

# References and resources
- [Official Pytest documentation](https://docs.pytest.org/en/latest/contents.html)
- [Pytest resources](https://docs.pytest.org/en/latest/talks.html)
- [Testing Pythin applications with pytest - Tutorial](https://semaphoreci.com/community/tutorials/testing-python-applications-with-pytest)
- [Guru99 Pytest tutorial](https://www.guru99.com/pytest-tutorial.html)