from os_ import create_os

if __name__ == '__main__':
    simulated_os = create_os(program_file='jobs.txt')
    simulated_os.run()
