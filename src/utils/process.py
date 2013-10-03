from subprocess import Popen, PIPE, STDOUT

class InteractiveProcessException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class InteractiveProcess:

    def __init__(self, exeName):
        self.proc = Popen(exeName, stdout = PIPE, stdin = PIPE, stderr = PIPE)

    def __del__(self):
        self.proc.terminate()

    def communicate(self, input):
        self.proc.stdin.write(input + '\n')
        # FIXME sleep?
        return self.proc.stdout.readline().strip()