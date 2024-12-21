using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using LLMUnity;
using Unity.Sentis;
using System.IO;

public class Agent : MonoBehaviour
{
    public LLMCharacter character; // Reference to the language model character
    public TextMeshProUGUI dialogue; // Reference for displaying dialogue text

    private string replyText; // Variable to store the full reply
    public string inputText;
    private bool hasPhenomeDictionary = true;
    private Dictionary<string, string> dict = new();

    private IWorker engine;
    private AudioClip clip;
    private const int samplerate = 22050;

    public Manager manager;

    private readonly string[] phonemes = new string[] {
        "<blank>", "<unk>", "AH0", "N", "T", "D", "S", "R", "L", "DH", "K", "Z", "IH1",
        "IH0", "M", "EH1", "W", "P", "AE1", "AH1", "V", "ER0", "F", ",", "AA1", "B",
        "HH", "IY1", "UW1", "IY0", "AO1", "EY1", "AY1", ".", "OW1", "SH", "NG", "G",
        "ER1", "CH", "JH", "Y", "AW1", "TH", "UH1", "EH2", "OW0", "EY2", "AO0", "IH2",
        "AE2", "AY2", "AA2", "UW0", "EH0", "OY1", "EY0", "AO2", "ZH", "OW2", "AE0", "UW2",
        "AH2", "AY0", "IY2", "AW2", "AA0", "\"", "ER2", "UH2", "?", "OY2", "!", "AW0",
        "UH0", "OY0", "..", "<sos/eos>" };

    void Start()
    {
        Debug.Log("Starting Agent"); // Optional for debugging
        LoadModel();
        ReadDictionary();
    }

    void LoadModel()
    {
        var model = ModelLoader.Load(Path.Join(Application.streamingAssetsPath, "jets-text-to-speech.sentis"));
        engine = WorkerFactory.CreateWorker(BackendType.GPUCompute, model);
    }

    void ReplyCompleted()
    {
        // Reply is completed, so trigger TTS with the full reply
        Debug.Log("The AI replied");
        manager.LogConversation(this.name, "player", replyText);
        Debug.Log("LLM Reply: " + replyText); // Optional for debugging
        TextToSpeech();
    }

    void HandleReply(string reply)
    {
        // Store the AI reply in replyText
        replyText = reply;
        dialogue.text = reply;
    }

    public void ReceivePlayerMessage(string message)
    {
        // Generate a reply based on the player's message
        _ = character.Chat(message, HandleReply, ReplyCompleted);
    }

    void TextToSpeech()
    {
        inputText = replyText;  // Use the full reply text for TTS
        string ptext = hasPhenomeDictionary ? TextToPhonemes(inputText) : "DH AH0 K W IH1 K B R AW1 N F AA1 K S JH AH1 M P S OW1 V ER0 DH AH0 L EY1 Z IY0 D AO1 G .";
        DoInference(ptext);
    }

    void ReadDictionary()
    {
        if (!hasPhenomeDictionary) return;
        string[] words = File.ReadAllLines(Path.Join(Application.streamingAssetsPath, "phoneme_dict.txt"));
        foreach (var s in words)
        {
            string[] parts = s.Split();
            if (parts[0] != ";;;")
            {
                string key = parts[0];
                dict.Add(key, s.Substring(key.Length + 2));
            }
        }
        dict.Add(",", ",");
        dict.Add(".", ".");
        dict.Add("!", "!");
        dict.Add("?", "?");
        dict.Add("\"", "\"");
    }

    public string ExpandNumbers(string text)
    {
        return text
            .Replace("0", " ZERO ")
            .Replace("1", " ONE ")
            .Replace("2", " TWO ")
            .Replace("3", " THREE ")
            .Replace("4", " FOUR ")
            .Replace("5", " FIVE ")
            .Replace("6", " SIX ")
            .Replace("7", " SEVEN ")
            .Replace("8", " EIGHT ")
            .Replace("9", " NINE ");
    }

    public string TextToPhonemes(string text)
    {
        string output = "";
        text = ExpandNumbers(text).ToUpper();

        string[] words = text.Split();
        foreach (var word in words)
        {
            output += DecodeWord(word);
        }
        return output;
    }

    public string DecodeWord(string word)
    {
        string output = "";
        int start = 0;
        for (int end = word.Length; end >= 0 && start < word.Length; end--)
        {
            if (end <= start)
            {
                start++;
                end = word.Length + 1;
                continue;
            }
            string subword = word.Substring(start, end - start);
            if (dict.TryGetValue(subword, out string value))
            {
                output += value + " ";
                start = end;
                end = word.Length + 1;
            }
        }
        return output;
    }

    int[] GetTokens(string ptext)
    {
        string[] p = ptext.Split();
        var tokens = new int[p.Length];
        for (int i = 0; i < tokens.Length; i++)
        {
            tokens[i] = Mathf.Max(0, System.Array.IndexOf(phonemes, p[i]));
        }
        return tokens;
    }

    public void DoInference(string ptext)
    {
        int[] tokens = GetTokens(ptext);

        using var input = new TensorInt(new TensorShape(tokens.Length), tokens);
        var result = engine.Execute(input);

        var output = result.PeekOutput("wav") as TensorFloat;
        output.CompleteOperationsAndDownload();
        var samples = output.ToReadOnlyArray();

        clip = AudioClip.Create("voice audio", samples.Length, 1, samplerate, false);
        clip.SetData(samples, 0);

        Speak();
    }

    private void Speak()
    {
        AudioSource audioSource = GetComponent<AudioSource>();
        if (audioSource != null)
        {
            audioSource.clip = clip;
            audioSource.Play();
        }
        else
        {
            Debug.LogWarning("No AudioSource component found on the GameObject.");
        }
    }

    private void OnDestroy()
    {
        engine?.Dispose();
    }
}
