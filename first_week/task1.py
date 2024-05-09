import argparse

def extract_numbers(x):
    float_list = []
    odd_list = []
    even_list = []

    current = ''
    for char in x:
        if char.isdigit() or char == '.':
            current += char
        elif current:
            if '.' in current:
                float_list.append(float(current))
            elif int(current) % 2 == 0:
                even_list.append(int(current))
            else:
                odd_list.append(int(current))
            current = ''
    
    if current:
        if '.' in current:
            float_list.append(float(current))
        elif int(current) % 2 == 0:
            even_list.append(int(current))
        else:
            odd_list.append(int(current))

    return float_list, odd_list, even_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract numbers from a given string.")
    parser.add_argument("input_string", type=str, help="Input string containing numbers")
    args = parser.parse_args()
    
    float_list, odd_list, even_list = extract_numbers(args.input_string)
    
    print("Float number:", float_list)
    print("Odd number:", odd_list)
    print("Even number:", even_list)
