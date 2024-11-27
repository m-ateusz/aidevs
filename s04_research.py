import numpy as np
from scipy.spatial import distance

def load_points(file_path):
    """Wczytuje punkty z pliku i zwraca je jako listę numpy array."""
    with open(file_path, 'r') as file:
        points = [np.array(list(map(int, line.strip().split(',')))) for line in file]
    return points

def load_points_v(file_path):
    """Wczytuje punkty z pliku i zwraca je jako listę numpy array."""
    with open(file_path, 'r') as file:
        points = [np.array(list(map(int, line.strip().split('=')[1].split(',')))) for line in file]
    return points

def classify_point(point, correct_points, incorrect_points, k=3):
    """Klasyfikuje punkt na podstawie k najbliższych sąsiadów."""
    all_points = correct_points + incorrect_points
    all_labels = ['CORRECT'] * len(correct_points) + ['INCORRECT'] * len(incorrect_points)
    
    # Oblicz odległości
    distances = [distance.euclidean(point, p) for p in all_points]
    sorted_indices = np.argsort(distances)[:k]  # Indeksy k najbliższych sąsiadów
    
    # Licz głosy
    votes = {'CORRECT': 0, 'INCORRECT': 0}
    for idx in sorted_indices:
        votes[all_labels[idx]] += 1
    
    return 'CORRECT' if votes['CORRECT'] > votes['INCORRECT'] else 'INCORRECT'

def main():
    # Wczytanie danych
    correct_points = load_points('data/lab_data/correct.txt')
    incorrect_points = load_points('data/lab_data/incorrect.txt')
    verify_points = load_points_v('data/lab_data/verify.txt')

    # Klasyfikacja punktów z verify.txt
    results = []
    for point in verify_points:
        classification = classify_point(point, correct_points, incorrect_points)
        results.append((point, classification))

    # Wyświetlenie wyników
    for i, (point, classification) in enumerate(results):
        if classification=='CORRECT':
            print(f"{i+1:02} Punkt {point} -> Klasa: {classification}")

if __name__ == "__main__":
    main()
