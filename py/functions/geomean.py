import math

def calculate_geometric_mean(ownerships):
    """
    Calculate the geometric mean of ownership percentages.

    Parameters:
        ownerships (list of float): List of ownership percentages as decimals (e.g., 0.25 for 25%).

    Returns:
        float: The geometric mean of the ownership percentages.
    """
    if len(ownerships) == 0:
        raise ValueError("The ownership list cannot be empty.")
    if any(o <= 0 or o > 1 for o in ownerships):
        raise ValueError("Ownership percentages must be between 0 and 1 (exclusive).")

    # Compute the product of ownerships
    product = math.prod(ownerships)
    # Calculate the geometric mean
    return product ** (1 / len(ownerships))

def calculate_target_range(contest_size):
    """
    Calculate the target geometric mean range based on contest size.

    Parameters:
        contest_size (int): Total number of entries in the contest.

    Returns:
        tuple: A refined range of geometric means (low, high) for lineup uniqueness.
    """
    if contest_size <= 0:
        raise ValueError("Contest size must be a positive integer.")
    
    # Refined range for uniqueness
    low = 1 / (contest_size ** (1 / 8))  # 8 is the meaningful slots after FLEX overlap
    high = low * 1.25  # Narrower range for practicality
    return low, high

def main():
    print("NFL Classic DFS Geometric Mean Calculator\n")
    try:
        # Prompt user for contest size
        contest_size = int(input("Enter contest size (number of entries): "))
        if contest_size <= 0:
            raise ValueError("Contest size must be greater than 0.")
        
        # Calculate target range
        low, high = calculate_target_range(contest_size)
        print(f"\nRefined Target Geometric Mean Range for Uniqueness: {low:.4f} - {high:.4f}")
        
        # Prompt user for lineup ownerships
        print("\nNow, enter your lineup's ownership percentages as decimals (e.g., 0.25 for 25%).")
        ownerships = list(map(float, input("Enter ownership percentages (9 values): ").split()))
        
        if len(ownerships) != 9:
            raise ValueError("NFL Classic lineups must have exactly 9 players.")

        # Calculate the geometric mean of the lineup
        geo_mean = calculate_geometric_mean(ownerships)
        print(f"\nYour Lineup's Geometric Mean: {geo_mean:.4f}")
        
        # Check if the lineup is within the target range
        if low <= geo_mean <= high:
            print("Your lineup is within the target range for uniqueness!")
        elif geo_mean < low:
            print("Your lineup is very unique but might be too contrarian.")
        else:
            print("Your lineup may not be unique. Consider lowering ownerships.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

