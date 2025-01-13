import express from 'express';
import Groq from "groq-sdk";
import cors from 'cors';

const groqApiKey = ""
const groq = new Groq({ apiKey: groqApiKey });
const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());
app.post('/quiz-data', async (req, res) => {
  try {
    // Get the prompt from the request body
    const { prompt } = req.body;
    console.log('Received prompt:', req.body.prompt);
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }


    // Query Groq with the received prompt
    const quizData = await groq.chat.completions.create({
        messages: [
          {
            role: "user",
            content: prompt,
          },
        ],
        model: 'llama-3.1-70b-versatile',
      });

    // Send the quiz data back as JSON
    res.json(quizData["choices"][0]["message"]["content"]);
  } catch (error) {
    console.error('Error fetching quiz data:', error);
    res.status(500).json({ error: error });
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});

