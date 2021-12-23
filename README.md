
# Simple .h and .cpp file generator

UI Python application to create .h and .cpp files easily.

1. Start the app with 'python filegen.py' command.
2. Enter the namespace name(s) separated by space, e.g. `math core` to create `math::core::ClassName`.
3. Enter the class name, e.g. `MyClassName`, 6 or more letters.
4. Push 'Create file(s)', MyClassName.h and MyClassName.cpp are created.
5. If the class name start with I letter (e.g. `IOperation`, it is consider an interface. Only a header is created in this case.
