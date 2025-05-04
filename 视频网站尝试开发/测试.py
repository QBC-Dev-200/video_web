class Test:
    def __init__(self):
        self.a=0
        print('init')
    def __enter__(self):
        self.a=1
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.a=0
        print('exit')
        return True
    
with Test() as f:
    print(f.a)


