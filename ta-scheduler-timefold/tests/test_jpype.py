import jpype
import os
import sys

jvm_path = os.path.join(
    os.environ["JAVA_HOME"],
    "lib",
    "server",
    "libjvm.dylib"
)

print(f"Trying to start JVM at: {jvm_path}")
print("Is JVM already started?", jpype.isJVMStarted())

try:
    jpype.startJVM(jvm_path, convertStrings=True)
    print("✅ JVM started successfully")

    # Now import after JVM is confirmed up
    java_lang = jpype.JPackage('java').lang
    print("Java version:", java_lang.System.getProperty("java.version"))
except Exception as e:
    print("❌ Error occurred")
    print(e)
    sys.exit(1)


# Recommended to add this to any main function or script using timefold
    # import jpype
    # import os

    # # Always start JVM before using Timefold or any Java-backed feature
    # jvm_path = os.path.join(
    #     os.environ["JAVA_HOME"],
    #     "lib",
    #     "server",
    #     "libjvm.dylib"
    # )

    # if not jpype.isJVMStarted():
    #     jpype.startJVM(jvm_path, convertStrings=True)

    # # ✅ Now you're safe to import Timefold
    # from timefold_solver import ...  # your imports here