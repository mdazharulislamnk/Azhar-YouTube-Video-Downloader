from PIL import Image

# Input/output
INPUT = "logo.png"
OUTPUT = "azhar.ico"

# ICO sizes Windows uses
sizes = [256, 128, 64, 48, 32, 16]

def main():
    img = Image.open(INPUT).convert("RGBA")
    img.save(OUTPUT, sizes=[(s, s) for s in sizes])
    print(f"Saved {OUTPUT} with sizes {sizes}")

if __name__ == "__main__":
    main()
