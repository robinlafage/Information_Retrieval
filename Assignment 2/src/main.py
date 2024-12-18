import argparse
from reranker import reranker
from train import train

def main():
    command, args = readCommandLineArgs()

    if command == 1:
        reranker(modelFile=args.model, medline=args.medline, inputFile=args.inputFile, outputFile=args.outputFile)
    elif command == 0:
        train(medline=args.medline, questions=args.training_data, outputFile=args.outputFile, gloveFile=args.gloveFile)
    else:
        print("Error")


def readCommandLineArgs():
    argsParser = argparse.ArgumentParser(
        description='A neural reranker for the second assignment of the RI course at Universidade de Aveiro'
    )

    # Define global arguments
    argsParser.add_argument("--train", action="store_true", help="Train the reranker instead of reranking")

    # Parse arguments to check for --train early
    args, remaining_args = argsParser.parse_known_args()

    if args.train:
        # Train mode
        trainParser = argparse.ArgumentParser(
            description='Train the reranker'
        )
        trainParser.add_argument("medline", type=str, help="Meline file")
        trainParser.add_argument("training_data", type=str, help="Training data file")
        trainParser.add_argument("outputFile", type=str, help="Output file to save the model")
        trainParser.add_argument("-g", "--gloveFile", type=str, help="Glove file", default="../model_data/glove.6B.50d.txt")
        return 0, trainParser.parse_args(remaining_args)
    else:
        # Rerank mode
        rerankParser = argparse.ArgumentParser(
            description='Rerank the results of a search engine'
        )
        rerankParser.add_argument("inputFile", type=str, help="Input file to rerank")
        rerankParser.add_argument("outputFile", type=str, help="Output file to save the reranked results")
        rerankParser.add_argument("medline", type=str, help="Medline file")
        rerankParser.add_argument("-m", "--model", type=str, help="Model to use for reranking", default="../model_data/model.pth")
        return 1, rerankParser.parse_args(remaining_args)

if __name__ == "__main__":
    main()