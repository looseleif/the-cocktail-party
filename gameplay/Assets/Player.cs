using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.IO;
using HuggingFace.API;

public class Player : MonoBehaviour
{
    private float moveSpeed = 50f;       // Speed of player movement
    private float smoothSpeed = 0.15f;  // Speed of smoothing for movement
    private Vector2 movement;           // Stores movement input
    private Rigidbody2D rb;             // Rigidbody for smooth movement
    private Agent currentAgent;         // The agent the player is interacting with

    [SerializeField] private TextMeshProUGUI text; // Display text for recording and messages

    private AudioClip clip;
    private byte[] bytes;
    private bool recording;

    public Manager manager;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>(); // Reference the Rigidbody2D
    }

    void Update()
    {
        // Get input for movement
        movement.x = Input.GetAxisRaw("Horizontal"); // A/D or Left/Right Arrow keys
        movement.y = Input.GetAxisRaw("Vertical");   // W/S or Up/Down Arrow keys

        // Toggle speech recording with T key, only if within range of an agent
        if (Input.GetKeyDown(KeyCode.T) && currentAgent != null)
        {
            if (recording)
            {
                StopRecording();
            }
            else
            {
                StartRecording();
            }
        }

        // Rotate player to face mouse cursor
        RotateTowardsMouse();

        // Automatically stop recording if audio reaches max length
        if (recording && Microphone.GetPosition(null) >= clip.samples)
        {
            StopRecording();
        }
    }

    void FixedUpdate()
    {
        // Smooth movement
        Vector2 targetPosition = (Vector2)transform.position + movement.normalized * moveSpeed * Time.fixedDeltaTime;
        rb.MovePosition(Vector2.Lerp(transform.position, targetPosition, smoothSpeed));
    }

    void RotateTowardsMouse()
    {
        // Get the mouse position in world space
        Vector3 mousePos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
        mousePos.z = 0;  // Ensure z is zero since we're in 2D

        // Calculate the direction to look at
        Vector2 direction = (mousePos - transform.position).normalized;

        // Calculate the angle and rotate the player to face the mouse
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        transform.rotation = Quaternion.Euler(new Vector3(0, 0, angle - 90)); // -90 to adjust orientation
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        // Check if the collider belongs to an Agent
        Agent agent = other.GetComponent<Agent>();
        if (agent != null)
        {
            currentAgent = agent;
            Debug.Log("Player is near " + agent.name);
        }
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        // Check if the collider belongs to the current agent
        Agent agent = other.GetComponent<Agent>();
        if (agent != null && currentAgent == agent)
        {
            Debug.Log("Player left conversation range of " + agent.name);
            currentAgent = null;

            // Stop recording if the player moves out of range while recording
            if (recording)
            {
                StopRecording();
            }
        }
    }

    // Speech recognition functionality
    private void StartRecording()
    {
        text.color = Color.red;  // Change text color to red when recording
        text.text = "Recording...";
        clip = Microphone.Start(null, false, 10, 44100);
        recording = true;
    }

    private void StopRecording()
    {
        var position = Microphone.GetPosition(null);
        Microphone.End(null);
        var samples = new float[position * clip.channels];
        clip.GetData(samples, 0);
        bytes = EncodeAsWAV(samples, clip.frequency, clip.channels);
        recording = false;
        text.color = Color.white;  // Change text color back to white
        text.text = "Processing...";
        SendRecording();
    }

    private void SendRecording()
    {
        text.color = Color.yellow;
        text.text = "Sending...";
        // Call HuggingFace API for speech-to-text
        HuggingFaceAPI.AutomaticSpeechRecognition(bytes, response =>
        {
            text.color = Color.white;
            text.text = response;
            manager.LogConversation(this.name, currentAgent?.name, response);
            currentAgent?.ReceivePlayerMessage(response); // Send the recognized speech to the Agent
        }, error =>
        {
            text.color = Color.red;
            text.text = error;
        });
    }

    private byte[] EncodeAsWAV(float[] samples, int frequency, int channels)
    {
        using (var memoryStream = new MemoryStream(44 + samples.Length * 2))
        {
            using (var writer = new BinaryWriter(memoryStream))
            {
                writer.Write("RIFF".ToCharArray());
                writer.Write(36 + samples.Length * 2);
                writer.Write("WAVE".ToCharArray());
                writer.Write("fmt ".ToCharArray());
                writer.Write(16);
                writer.Write((ushort)1);
                writer.Write((ushort)channels);
                writer.Write(frequency);
                writer.Write(frequency * channels * 2);
                writer.Write((ushort)(channels * 2));
                writer.Write((ushort)16);
                writer.Write("data".ToCharArray());
                writer.Write(samples.Length * 2);

                foreach (var sample in samples)
                {
                    writer.Write((short)(sample * short.MaxValue));
                }
            }
            return memoryStream.ToArray();
        }
    }
}
