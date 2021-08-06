symbol = "TSLA_011521C650"
symbolParts = symbol.split("_")
symbolWithDate = symbolParts[0]+"_"+symbolParts[1][:6]
print(symbolWithDate)
print(symbolParts[1][7:]+".0")
