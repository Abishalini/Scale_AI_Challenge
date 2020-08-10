import scaleapi

client = scaleapi.ScaleClient('live_953b8b2557c6492c92f79c7b5a4fdcf6')

tasks = client.tasks(project="Traffic Sign Detection")