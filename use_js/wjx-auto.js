(function() {
    'use strict';
    // Example probability table for each question
    var probabilities = {
        1: [0.1, 0.9], // Probabilities for answers of question 1
        2: [0.5, 0.5], // Probabilities for answers of question 2
        // Add more probabilities for other questions
    };

    // Function to select an answer based on probabilities
    function chooseAnswer(probArray) {
        let total = probArray.reduce((acc, val) => acc + val, 0);
        let random = Math.random() * total;
        let sum = 0;

        for (let i = 0; i < probArray.length; i++) {
            sum += probArray[i];
            if (random < sum) {
                return i; // Return index of the chosen answer
            }
        }
        return 0; // Default to the first answer if something goes wrong
    }

    function judgeAndAnswerQuestions() {
        var questions = document.getElementsByClassName("field ui-field-contain");
;
        console.log(1)
        Array.from(questions).forEach((question, index) => {
            console.log(1)
            let qIndex = index + 1; // Question numbers typically start from 1
            let choices = question.querySelectorAll("input[type='radio'], input[type='checkbox']");

            if (probabilities[qIndex]) {
                let answerIndex = chooseAnswer(probabilities[qIndex]);
                choices[answerIndex].click(); // Select the answer based on the chosen index
            } else {
                // If no probabilities are defined, randomly select an answer
                choices[Math.floor(Math.random() * choices.length)].click();
            }
        });
    }

    judgeAndAnswerQuestions();

    // You may want to handle the form submission or navigation differently depending on your needs
})();
