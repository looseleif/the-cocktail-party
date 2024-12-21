using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.IO;
using System.Collections;
using UnityEngine.Networking;

public class Manager : MonoBehaviour
{
    [Header("UI Elements")]
    public Button uploadLogButton;               // Button for uploading the log file
    public Button sendButton;                    // Button for sending data to the server
    public TextMeshProUGUI logPreviewText;       // Preview text for the loaded log
    public TextMeshProUGUI responseText;         // Response text from the server

    [Header("Conversation Data")]
    private ConversationLog conversationLog = new ConversationLog(); // Structured log
    public string flaskServerUrl = "http://localhost:5000/process";  // API endpoint
    private string persistentLogFile;                                 // Path for the persistent log file

    void Start()
    {
        // Initialize the persistent log file path
        persistentLogFile = Application.dataPath + "/conversation_log_persistent.json";

        // Add listeners to buttons
        uploadLogButton.onClick.AddListener(UploadLogFile);
        sendButton.onClick.AddListener(SendConversationLog);

        // Optionally, load existing log file
        LoadPersistentLog();
    }

    public void LogConversation(string sender, string receiver, string content)
    {
        // Find an existing conversation or create a new one
        Conversation conversation = conversationLog.conversations.Find(c =>
            (c.participantA == sender && c.participantB == receiver) ||
            (c.participantA == receiver && c.participantB == sender));

        if (conversation == null)
        {
            conversation = new Conversation(sender, receiver);
            conversationLog.conversations.Add(conversation);
        }

        // Add the message to the conversation
        Message newMessage = new Message(sender, content);
        conversation.messages.Add(newMessage);

        // Persist the message to the log file
        AppendMessageToFile(sender, receiver, newMessage);

        // Update the UI preview
        logPreviewText.text = $"Latest: {sender} -> {receiver}: {content}";
    }

    void UploadLogFile()
    {
        // Save the full conversation log to a JSON file
        string filePath = Application.dataPath + "/conversation_log_persistent.json";
        string json = JsonUtility.ToJson(conversationLog, true);
        File.WriteAllText(filePath, json);

        logPreviewText.text = $"Log saved to: {filePath}\nPreview:\n{json}";
    }

    void AppendMessageToFile(string sender, string receiver, Message message)
    {
        // Prepare a log entry for appending
        string logEntry = $"{{ \"timestamp\": \"{message.timestamp}\", \"sender\": \"{sender}\", \"receiver\": \"{receiver}\", \"content\": \"{message.content}\" }}";

        // Append the log entry to the persistent file
        File.AppendAllText(persistentLogFile, logEntry + ",\n");
    }

    void LoadPersistentLog()
    {
        if (File.Exists(persistentLogFile))
        {
            string existingLog = File.ReadAllText(persistentLogFile);
            Debug.Log($"Loaded existing log:\n{existingLog}");
        }
    }

    void SendConversationLog()
    {
        if (conversationLog.conversations.Count == 0)
        {
            responseText.text = "No conversations to send.";
            return;
        }

        StartCoroutine(SendDataToServer(JsonUtility.ToJson(conversationLog)));
    }

    IEnumerator SendDataToServer(string json)
    {
        UnityWebRequest request = new UnityWebRequest(flaskServerUrl, "POST");
        request.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json));
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            responseText.text = $"Response: {request.downloadHandler.text}";
        }
        else
        {
            responseText.text = $"Error: {request.error}";
        }
    }
}

[System.Serializable]
public class Message
{
    public string sender;
    public string content;
    public string timestamp;

    public Message(string sender, string content)
    {
        this.sender = sender;
        this.content = content;
        this.timestamp = System.DateTime.UtcNow.ToString("o"); // ISO 8601
    }
}

[System.Serializable]
public class Conversation
{
    public string participantA;
    public string participantB;
    public List<Message> messages;

    public Conversation(string participantA, string participantB)
    {
        this.participantA = participantA;
        this.participantB = participantB;
        this.messages = new List<Message>();
    }
}

[System.Serializable]
public class ConversationLog
{
    public List<Conversation> conversations = new List<Conversation>();
}
