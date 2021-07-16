"""main entry for langlab command-line interface"""

def main():
    from langlab import Langlab
    ret, fwds = Langlab().run_command()

if __name__ == "__main__":
    main()
