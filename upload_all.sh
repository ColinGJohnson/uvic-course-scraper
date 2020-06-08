
for filename in ./json/*.json; do
    echo "uploading $filename..."
    python3 ./Uploader.py --input="$filename" --constr="mongodb+srv://$mongouser:$mongopass@cluster0-do46y.mongodb.net/?retryWrites=true&w=majority"
done
