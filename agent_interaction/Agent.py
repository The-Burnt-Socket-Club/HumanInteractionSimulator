import random
import numpy as np # Though numpy isn't directly used in this snippet, it's good practice to keep it if there are plans.

class Group:

    pass
class Relationship:
    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2
        self.strength = random.uniform(0.5, 1.0) # Initial strength
        # ... other relationship attributes (e.g., type, duration)

    def __repr__(self):
        return f"Relationship({self.agent1.age}-{self.agent2.age}, Str:{self.strength:.2f})"


class Agent:
    # Physical and Intellectual Characteristics
    groups = [] # Class variable, careful with mutable defaults
    age = None
    gender = None
    iq = None
    eq = None
    physical_fitness = None
    physical_health = None
    knowledge = None
    linguistic_ability = None
    likeability = None

    # Emotional and Mental traits
    loner_score = None
    open_to_trust_score = None

    # Memory characteristics
    experiences = [] # Class variable, careful with mutable defaults
    relationships = [] # Class variable, careful with mutable defaults
    # groups = [] # Duplicate, remove this if groups is intended as a class variable

    _MAX_AGE = 100 # Maximum simulated age

    # Conceptual Fertility Rates (Births per 1000 women per year)
    # Key: age group start (for female agents) : fertility rate
    _FERTILITY_RATES = {
        15: 10,
        20: 80,
        25: 120,
        30: 100,
        35: 60,
        40: 20,
        45: 5
    }

    _MALE_BIRTH_RATIO = 0.51 # Probability of a newborn being male

    # Conceptual Mortality Rates (Probability of dying in a year)
    # Key: age : probability of dying for male, probability of dying for female

    _MORTALITY_RATES = {
        0: (0.005, 0.004), # Infant mortality
        1: (0.001, 0.0008), # Child mortality (1-4 years)
        5: (0.0005, 0.0004), # Child mortality (5-9 years)
        10: (0.0002, 0.0001), # Low mortality for youth
        15: (0.0005, 0.0002), # Slight increase in adolescence
        20: (0.001, 0.0003), # Young adult mortality
        30: (0.0015, 0.0005),
        40: (0.003, 0.001),
        50: (0.008, 0.004),
        60: (0.02, 0.01),
        70: (0.05, 0.03),
        80: (0.15, 0.10),
        90: (0.35, 0.25),
        100: (1.0, 1.0) # Certain death at 100+
    }

    # Parameters for Physical Fitness vs. Age model (conceptual)
    _FITNESS_PEAK_START_AGE = 20
    _FITNESS_PEAK_END_AGE = 30
    _FITNESS_PEAK_VALUE = 90
    _FITNESS_GROWTH_RATE = _FITNESS_PEAK_VALUE / _FITNESS_PEAK_START_AGE
    _FITNESS_DECLINE_RATE = 0.8 # Adjusted for 0-100 scale
    _FITNESS_MIN_FLOOR = 10
    _FITNESS_STD_DEV = 10

    # These should ideally be instance variables or passed to the agent
    # if you want each agent to have its own Q-table and learning parameters.
    # For a shared Q-table for all agents, they remain class variables.
    Q_table = {} # A dictionary to store Q-values: (state_tuple) -> {action: Q_value}
    learning_rate = 0.1
    discount_factor = 0.95
    exploration_rate = 0.1 # Epsilon-greedy

    # Reward definitions (could be class constants)
    R_FORM_RELATIONSHIP = 10
    P_BREAK_RELATIONSHIP = -5
    R_SURVIVAL_PER_YEAR = 1
    P_DEATH = -100


    def __init__(self, age=None, gender=None):
        # Assign age and gender. If not provided, initialize as a newborn.
        if age is None:
            self.age = 0 # Newborn
            self.gender = 'Male' if random.random() < self._MALE_BIRTH_RATIO else 'Female'
        else:
            self.age = age
            self.gender = gender if gender else ('Male' if random.random() < 0.5 else 'Female') # Random if not specified

        # Initialize other characteristics, some depending on age/gender
        self.iq = min(max(random.gauss(100, 15), 50), 150)
        self.eq = min(max(random.gauss(75, 12), 0), 100)

        mean_fitness_for_age = self._calculate_mean_physical_fitness(self.age)
        self.physical_fitness = min(max(random.gauss(mean_fitness_for_age, self._FITNESS_STD_DEV), 0), 100)

        self.physical_health = min(max(random.gauss(70, 10), 0), 100)
        self.knowledge = min(max(self.iq + random.gauss(0, 10), 0), 150)
        self.linguistic_ability = min(max(self.iq + random.gauss(0, 10), 0), 150)
        self.likeability = min(max(self.eq + random.gauss(0, 10), 0), 100)
        self.loner_score = min(max(random.gauss(50, 15), 0), 100)
        self.open_to_trust_score = min(max(random.gauss(50, 15), 0), 100)

        # Ensure these are instance variables, not class variables (mutable defaults)
        self.experiences = []
        self.relationships = []
        self.groups = []

        self.last_state = None
        self.last_action = None

    def _get_state(self):
        # Discretize continuous attributes for Q-table
        age_group = min(self.age // 10, 9) # 0-9, 10-19, ..., 90+
        eq_group = int(min(self.eq // 20, 4)) # Explicitly cast to int
        loner_group = int(min(self.loner_score // 20, 4)) # Explicitly cast to int
        trust_group = int(min(self.open_to_trust_score // 20, 4)) # Explicitly cast to int
        num_relationships_group = min(len(self.relationships) // 2, 4) # This will be int as len() returns int
        health_group = int(min(self.physical_health // 20, 4)) # Explicitly cast to int

        return (age_group, eq_group, loner_group, trust_group, num_relationships_group, health_group)

    def choose_action(self, available_agents):
        state = self._get_state() # Get current state
        # Ensure the current state exists in Q_table before accessing it
        if state not in self.Q_table:
            self.Q_table[state] = {
                'no_action': 0.0,
                'form_relationship': 0.0, # Attempt to form a relationship
                'break_relationship': 0.0 # Attempt to break a relationship
            }
        self.last_state = state # Store this state as the state from which the action was chosen

        # Epsilon-greedy strategy
        if random.random() < self.exploration_rate:
            return random.choice(list(self.Q_table[state].keys()))
        else:
            # Choose action with highest Q-value
            return max(self.Q_table[state], key=self.Q_table[state].get)

    def perform_action(self, action, all_agents):
        reward = 0
        relationship_formed_this_turn = False
        relationship_broken_this_turn = False

        if action == 'form_relationship':
            # Try to find a suitable partner that's not already in a relationship
            potential_partners = [
                a for a in all_agents
                if a != self and a not in [r.agent1 if r.agent2 == self else r.agent2 for r in self.relationships]
            ]
            if potential_partners:
                partner = random.choice(potential_partners)
                # Logic for successful relationship formation (e.g., based on likeability, compatibility)
                if self.likeability + partner.likeability > random.uniform(50, 150): # Simple compatibility check
                    new_relationship = Relationship(self, partner)
                    self.relationships.append(new_relationship)
                    partner.relationships.append(new_relationship) # Add to partner's relationships as well
                    reward += self.R_FORM_RELATIONSHIP
                    relationship_formed_this_turn = True
        elif action == 'break_relationship':
            if self.relationships:
                rel_to_break = random.choice(self.relationships)
                self.relationships.remove(rel_to_break)
                # Also remove from the other agent's relationships
                other_agent = rel_to_break.agent1 if rel_to_break.agent2 == self else rel_to_break.agent2
                # Check if other_agent is still in population and has the relationship
                if other_agent in all_agents and rel_to_break in other_agent.relationships:
                    other_agent.relationships.remove(rel_to_break)
                reward += self.P_BREAK_RELATIONSHIP
                relationship_broken_this_turn = True
        elif action == 'no_action':
            pass # No specific immediate reward for no action, unless you want to model a small time penalty or maintenance cost.


        self.last_action = action # Store the chosen action

        return reward, relationship_formed_this_turn, relationship_broken_this_turn

    def learn(self, current_reward, new_state, is_terminal=False):
        if self.last_state is None or self.last_action is None:
            return # No previous action to learn from

        # This check is still good, as new_state might be truly new
        if new_state not in self.Q_table:
            self.Q_table[new_state] = {
                'no_action': 0.0,
                'form_relationship': 0.0,
                'break_relationship': 0.0
            }

        old_q_value = self.Q_table[self.last_state][self.last_action] # Now self.last_state should be in Q_table

        if is_terminal: # If agent died
            next_max_q = 0
        else:
            next_max_q = max(self.Q_table[new_state].values())

        # Q-learning update rule
        self.Q_table[self.last_state][self.last_action] = (
            old_q_value + self.learning_rate * (current_reward + self.discount_factor * next_max_q - old_q_value)
        )
        # self.last_state and self.last_action are now updated by choose_action for the next step,
        # so no need to reset them here.

    def _calculate_mean_physical_fitness(self, age):
        if age < self._FITNESS_PEAK_START_AGE:
            mean_fitness = self._FITNESS_GROWTH_RATE * age
        elif self._FITNESS_PEAK_START_AGE <= age <= self._FITNESS_PEAK_END_AGE:
            mean_fitness = self._FITNESS_PEAK_VALUE
        else:
            decline_amount = self._FITNESS_DECLINE_RATE * (age - self._FITNESS_PEAK_END_AGE)
            mean_fitness = self._FITNESS_PEAK_VALUE - decline_amount
        return max(mean_fitness, self._FITNESS_MIN_FLOOR)

    def is_alive(self):
        """Determines if the agent survives another year based on mortality rates."""
        if self.age >= self._MAX_AGE: # Max age reached
            return False

        # Find the appropriate mortality rate for this age and gender
        age_group_start = next((a for a in sorted(self._MORTALITY_RATES.keys()) if a <= self.age), 0)
        male_mortality_rate, female_mortality_rate = self._MORTALITY_RATES[age_group_start]

        mortality_prob = male_mortality_rate if self.gender == 'Male' else female_mortality_rate

        # Add some randomness based on physical health: lower health slightly increases mortality risk
        health_factor = (100 - self.physical_health) / 100 # 0 if health is 100, 1 if health is 0
        mortality_prob += mortality_prob * health_factor * 0.1 # Small increase based on poor health

        return random.random() > mortality_prob # If random number is greater than probability, agent survives

    def can_reproduce(self):
        """Checks if the agent is a female of reproductive age."""
        return self.gender == 'Female' and 15 <= self.age <= 49

    def get_fertility_rate(self):
        """Returns the fertility rate for the agent's age group."""
        if not self.can_reproduce():
            return 0
        age_group_start = next((a for a in sorted(self._FERTILITY_RATES.keys(), reverse=True) if a <= self.age), 0)
        return self._FERTILITY_RATES.get(age_group_start, 0)

    def grow_older(self):
        self.age += 1
        mean_fitness_for_age = self._calculate_mean_physical_fitness(self.age)
        current_fitness_deviation = self.physical_fitness - mean_fitness_for_age
        self.physical_fitness = min(max(mean_fitness_for_age + current_fitness_deviation * 0.9 + random.gauss(0, self._FITNESS_STD_DEV * 0.1), 0), 100)
        # You might also add health decay here
        self.physical_health = max(0, self.physical_health - random.uniform(0.1, 1.0)) # Example of health decline

    def __str__(self):
        return (
            f"Agent:\n"
            f"  Age: {self.age}\n"
            f"  Gender: {self.gender}\n"
            f"  IQ: {self.iq:.1f}\n"
            f"  EQ: {self.eq:.1f}\n"
            f"  Physical Fitness: {self.physical_fitness:.1f}\n"
            f"  Physical Health: {self.physical_health:.1f}\n"
            f"  Knowledge: {self.knowledge:.1f}\n"
            f"  Linguistic Ability: {self.linguistic_ability:.1f}\n"
            f"  Likeability: {self.likeability:.1f}\n"
            f"  Loner Score: {self.loner_score:.1f}\n"
            f"  Open to Trust Score: {self.open_to_trust_score:.1f}\n"
            f"  Experiences: {len(self.experiences)}\n"
            f"  Relationships: {len(self.relationships)}\n"
            f"  Groups: {len(self.groups)}"
        )

    def __repr__(self):
        return f"Agent(Age={self.age}, Gender={self.gender}, Fitness={self.physical_fitness:.1f})"

class PopulationSimulator:
    def __init__(self, initial_population_size):
        self.population = []
        for _ in range(initial_population_size):
            age = random.randint(0, Agent._MAX_AGE // 2)
            gender = 'Male' if random.random() < 0.5 else 'Female'
            self.population.append(Agent(age=age, gender=gender))
        print(f"Initial population size: {len(self.population)}")

    def simulate_year(self):
        new_population = []
        births_this_year = 0
        deaths_this_year = 0

        current_agents = list(self.population) # Make a copy for iteration and interaction

        for agent in current_agents:
            # 1. Agent makes a decision based on RL
            # The choose_action method now stores agent.last_state
            action = agent.choose_action(current_agents)
            action_reward, _, _ = agent.perform_action(action, current_agents)

            # 2. Agent ages
            agent.grow_older()

            # 3. Check for mortality (including the large penalty for death)
            if not agent.is_alive():
                deaths_this_year += 1
                # Agent learns from its terminal state (death)
                agent.learn(Agent.P_DEATH, None, is_terminal=True)
                continue # Agent dies, not added to new_population

            # 4. Agent receives a survival reward and learns
            annual_reward = Agent.R_SURVIVAL_PER_YEAR + action_reward # Combine survival and action rewards
            new_state = agent._get_state() # Get the state *after* aging and potential health changes
            agent.learn(annual_reward, new_state) # Agent learns from the annual outcome

            new_population.append(agent) # Agent survives

            # 5. Check for births (only for reproducing females)
            if agent.can_reproduce():
                fertility_rate = agent.get_fertility_rate()
                birth_prob = fertility_rate / 1000.0
                if random.random() < birth_prob:
                    new_baby = Agent() # Newborn agent
                    new_population.append(new_baby)
                    births_this_year += 1

        # Handle Migration (simplified: just random immigration)
        num_immigrants = 5
        for _ in range(num_immigrants):
            age = random.randint(0, 40)
            gender = 'Male' if random.random() < 0.5 else 'Female'
            new_population.append(Agent(age=age, gender=gender))

        self.population = new_population
        print(f"Year End: Population={len(self.population)}, Births={births_this_year}, Deaths={deaths_this_year}")

# --- Run the Simulation ---
if __name__ == "__main__":
    simulator = PopulationSimulator(initial_population_size=1000)
    for year in range(10): # Simulate for 50 years to allow for some learning
        print(f"\n--- Simulating Year {year + 1} ---")
        simulator.simulate_year()
        # Optional: Print some agent details after a few years to see if behavior changes
        if year % 10 == 9:
            print(f"\n--- Sample Agents after Year {year + 1} ---")
            # Filter for agents that are still alive before printing
            alive_agents = [a for a in simulator.population if a.is_alive()]
            for i, agent in enumerate(alive_agents[:5]): # Print first 5 alive agents
                print(agent)
                print(f"  Relationships: {[str(r) for r in agent.relationships]}")

    ages_at_end = [agent.age for agent in simulator.population]
    import matplotlib.pyplot as plt
    plt.hist(ages_at_end, bins=range(0, Agent._MAX_AGE + 1, 5), edgecolor='black')
    plt.title('Age Distribution After Simulation')
    plt.xlabel('Age Group')
    plt.ylabel('Number of Agents')
    plt.show()

    # Analyze Q-table (for a single agent, or average across agents if learning shared)
    if simulator.population:
        # Get a sample agent that survived for analysis
        sample_agent = next((a for a in simulator.population if a.is_alive()), None)
        if sample_agent:
            print("\n--- Sample Agent Q-table (partial) ---")
            # Limit the output to avoid overwhelming if Q-table gets very large
            q_table_items = list(sample_agent.Q_table.items())
            for state, actions in q_table_items[:min(5, len(q_table_items))]: # Print up to 5 states
                print(f"State {state}:")
                for action, q_value in actions.items():
                    print(f"  {action}: {q_value:.2f}")
        else:
            print("\nNo agents survived to show Q-table.")