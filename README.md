# The Cocktail Party

## Overview
**The Cocktail Party** is a narrative-driven, social interaction game where players collaborate and compete to influence NPCs (Non-Player Characters) within a dynamically evolving scenario. Players are assigned unique roles, agendas, and items to create a rich, strategic gameplay experience.

The game includes the following key roles and components:

- **Players**: Attempt to persuade NPCs or spread/discredit specific narratives.
- **NPCs**: Communicative agents that propagate information and respond to players.
- **Overseer**: A game manager with omniscient knowledge of the scenario and player interactions.
- **Scenarios**: Narratives that provide the context for each game session.
- **Items**: Gameplay elements that introduce randomness and strategy.

## Game Mechanics

### Phases of Gameplay
1. **Briefing Phase**
   - Players receive context about the scenario.
   - Each player is assigned an agenda, a secret, and an item.
   - A set of "matters of fact" (MOF) is introduced, forming the backbone of the scenario.

2. **Coercion Phase**
   - Players interact with NPCs to influence them.
   - Players use their agendas, items, and knowledge of secrets to manipulate conversations.
   - NPCs have dynamic emotional states that evolve during the interaction.

3. **Convening Phase**
   - NPCs share their impressions with each other, forming a collective understanding.
   - The Overseer determines which players successfully influenced the NPCs and updates the game state.

4. **Resolution Phase**
   - Players receive feedback on their performance.
   - The scenario evolves based on player actions, leading to the next round or a conclusion.

5. **Replay Phase**
   - Players are offered the opportunity to replay the scenario or select a new one.
   - Additional insights or alternate paths can be explored based on previous decisions.

### Player Mechanics
- **Agendas**: Players are given a specific narrative or goal they must push during interactions.
- **Secrets**: Each player possesses a unique secret tied to the scenario’s MOF. They can use this to gain trust or deceive others.
- **Items**: Items provide strategic advantages or obstacles. Examples include:
  - **Truth Serum**: Forces an NPC to reveal their secret.
  - **Forged Evidence**: Plants false information into the narrative.

### NPC Mechanics
- **Dynamic Emotional States**:
  - NPCs have attributes such as:
    - **Happiness**
    - **Hunger**
    - **Attentiveness**
    - **Defensiveness**
    - **Curiosity**
  - These states evolve in response to player interactions, influencing their behavior.

- **Memory System**:
  - NPCs remember past interactions, forming biases toward players.

- **Communication Propagation**:
  - NPCs share information with each other, which may be distorted or misrepresented.

### Overseer Mechanics
- **Scenario Management**:
  - Provides the scenario’s initial context and updates it dynamically as the game progresses.

- **Game State Tracking**:
  - Monitors player actions, NPC responses, and evolving narratives.
  - Determines if players achieve their agendas.

- **NPC Behavior Management**:
  - Oversees NPC emotional state changes and their propagation of information.

- **Conversation Analysis**:
  - Tracks whether players achieved their goals by analyzing dialogue and determining persuasion effectiveness.
  - Evaluates if key target statements were accepted or rejected by NPCs.

- **Emotional Management**:
  - Monitors the change in NPC dynamics, such as shifts in trust or defensiveness, as the game progresses.
  - Uses these metrics to influence the narrative and provide feedback to players.

## Technical Design

### Backend Infrastructure
**The Cocktail Party** uses a unified **Intelligence Server** as the central hub to manage gameplay logic and interactions. This server:

1. **Monitors Active Game State**:
   - Tracks players, NPCs, and narrative progress in real-time.

2. **Creates Agent-Wise Conversations**:
   - Generates contextually appropriate dialogues using AI models.
   - Adjusts NPC emotional states dynamically based on interactions.

3. **Communicates with the Overseer**:
   - Updates game mechanics, evaluates player influence, and triggers narrative changes.

4. **Integrates with Unity Frontend**:
   - Provides real-time feedback and dialogue for immersive player interactions.

### Game Data
- **Scenario Data**:
  - Predefined narratives with associated MOF.

- **Agent Data**:
  - Includes NPC attributes, agendas, and emotional states.

- **Interaction Data**:
  - Tracks player-NPC interactions and updates NPC responses dynamically.

### Fine-Tuning for Sentiment Analysis and Fallacy Detection
- The backend uses open-source models fine-tuned on datasets for sentiment analysis and logical fallacy detection.
- **Open-Source Datasets**: Examples include:
  - **IMDB Sentiment Dataset** for dialogue tone analysis.
  - **ArguAna** for logical consistency.

- **Methods of Fine-Tuning**:
  - Retrain models with contextual data from gameplay logs.
  - Incorporate domain-specific scenarios to align NPC responses with narrative themes.

- **Fallacy Detection**:
  - Identifies misleading arguments or logical inconsistencies in player-NPC conversations.
  - Flags conversations with high fallacy likelihood for Overseer review.

### Fine-Tuning with Axolotl and Unsloth
To achieve optimal performance for in-game interactions, the backend leverages **Axolotl** and **Unsloth** for fine-tuning models:

1. **Axolotl**:
   - Provides an adaptable framework for fine-tuning large language models on game-specific datasets.
   - Used to train models to understand and replicate conversational dynamics, including nuanced NPC behaviors.
   - Supports integration with open-source datasets and custom gameplay logs to align with the game's narrative and interaction goals.

2. **Unsloth**:
   - Specializes in optimizing inference times and reducing latency during real-time gameplay.
   - Enhances the responsiveness of NPC interactions by pruning redundant model pathways while maintaining high fidelity in responses.

3. **Workflow**:
   - **Data Preparation**:
     - Gameplay logs and scenario-specific text are collected as training datasets.
     - Open-source data is preprocessed to fit narrative and interaction goals.
   - **Model Training**:
     - Axolotl is employed to fine-tune large language models to generate narrative-aligned conversations.
     - Unsloth optimizes these fine-tuned models for faster inference.
   - **Evaluation**:
     - Performance is measured against in-game metrics such as emotional state adaptation and fallacy detection accuracy.

## Key Systems
- **Dynamic Emotional State Generation**:
  - Uses the Outlines library to generate values for NPC attributes (happiness, hunger, etc.).

- **Scenario Evolution**:
  - Scenario updates are triggered based on player actions and NPC feedback.

- **Player-NPC Interaction Engine**:
  - Processes player dialogue and generates NPC responses using LLaMA and Outlines.

## Example Scenario
### Murder Mystery on a Cruise
- **Briefing Phase**:
  - Context: A wealthy tycoon has been murdered aboard a cruise ship.
  - MOF: Key facts include the tycoon’s last known location, the suspects, and the timeline of events.
  - Player Agendas:
    - Frame another player for the murder.
    - Uncover the truth and exonerate an innocent suspect.

- **Coercion Phase**:
  - Players interact with NPCs, such as:
    - The ship’s captain (authoritative).
    - A passenger (unreliable witness).
    - The tycoon’s business rival (defensive).

- **Convening Phase**:
  - NPCs discuss their impressions and decide which narratives seem most credible.

- **Resolution Phase**:
  - The Overseer determines the outcome based on NPC decisions and updates the scenario.

- **Replay Phase**:
  - Players revisit the scenario with new insights or select an alternate path.

## Future Improvements
- **Expanded Scenarios**:
  - Add more genres like political intrigue, corporate espionage, or alien diplomacy.
- **Enhanced NPC AI**:
  - Incorporate advanced memory and personality systems for NPCs.
- **Player Progression**:
  - Introduce unlockable items and scenarios based on player performance.
