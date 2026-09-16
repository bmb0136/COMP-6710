import sys

if __name__ == '__main__':
  try:
    file = open("data.csv", "r")
  except OSError:
    print("Unable to open file", file=sys.stderr)
    sys.exit(1)

  for line in file:
    line = line.rstrip('\n')
    tokens = line.split(',')
    column = 0

    for token in tokens:
      print(f"Row {column // 3}, Col {column % 3}: {token}")
      column += 1

  file.close()
  sys.exit(0)
