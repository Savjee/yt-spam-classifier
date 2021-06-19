import CreateML
import Foundation

let csv = Bundle.main.url(forResource: "rated-comments", withExtension: "csv")!
let parsingOptions = MLDataTable.ParsingOptions(containsHeader: true, delimiter: ";", doubleQuote: true)
var data = try MLDataTable(contentsOf: csv, options: parsingOptions)

let spamString = data["Spam"].map(to: String.self)
data.removeColumn(named: "Spam")
data.addColumn(spamString, named: "Spam")

data = data.dropMissing().dropDuplicates()

let (trainingData, testingData) = data.randomSplit(by: 0.8, seed: 5)
print(trainingData)

let sentimentClassifier = try MLTextClassifier(trainingData: trainingData,
                                               textColumn: "Comment",
                                               labelColumn: "Spam")

// Training accuracy as a percentage
let trainingAccuracy = (1.0 - sentimentClassifier.trainingMetrics.classificationError) * 100

// Validation accuracy as a percentage
let validationAccuracy = (1.0 - sentimentClassifier.validationMetrics.classificationError) * 100

let metadata = MLModelMetadata(author: "Xavier Decuyper",
                               shortDescription: "CoreML Model for YouTube spam",
                               version: "1.0")

try sentimentClassifier.write(to: URL(fileURLWithPath: "/Users/xavier/Desktop/yt-spam.mlmodel"),
                              metadata: metadata)
