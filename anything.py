from hed import HED  # Assume you install a library or implement HED

model = HED(pretrained=True)
edges = model.predict('image.jpg')