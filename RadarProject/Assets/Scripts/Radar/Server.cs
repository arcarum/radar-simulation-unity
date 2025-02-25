using UnityEngine;
using WebSocketSharp;
using WebSocketSharp.Server;

public class Server : MonoBehaviour
{
    public static Server serverInstance;
    public WebSocketServer server;

    void Awake()
    {
        Debug.Log("Server awake");
        serverInstance = this;

        if (server == null)
            server = new WebSocketServer("ws://localhost:8080");
    }

    // Start is called before the first frame update
    void Start()
    {
        server.Start();
        Debug.Log("Started Server");
    }

    void OnDestroy()
    {
        server.Stop();
        Debug.Log("Stopped Server");

    }

    void OnApplicationQuit()
    {
        server.Stop();
        Debug.Log("Stopped Server");
    }
}

public class DataService : WebSocketBehavior
{
    protected override void OnMessage(MessageEventArgs e)
    {
        // Handle incoming messages if needed
        Debug.Log($"Received message: {e.Data}");
    }

    protected override void OnOpen()
    {
        Debug.Log("Client connected");
    }

    protected override void OnClose(CloseEventArgs e)
    {
        Debug.Log("Client disconnected");
    }

    protected override void OnError(ErrorEventArgs e)
    {
        Debug.LogError($"WebSocket error: {e.Message}");
    }
}
