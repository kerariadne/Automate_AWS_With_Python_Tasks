import argparse

def is_armstrong(num):
    sum = 0
    power = 0
    num_str = str(num)
    num_digits = len(num_str)
    for digit in num_str:
        power = pow(int(digit),num_digits)
        sum += power
        
    return sum == num

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find Armstrong numbers between a specified range.")
    parser.add_argument("start", type=int, help="Start of the range")
    parser.add_argument("end", type=int, help="End of the range")
    args = parser.parse_args()
    
    print(f"Armstrong numbers between {args.start} and {args.end}:")
    for num in range(args.start, args.end + 1):
        if is_armstrong(num):
            print(num)
