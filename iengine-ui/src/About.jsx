import React from 'react';

const About = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-sky-400 to-blue-900 text-white">
      <div className="bg-white bg-opacity-10 backdrop-blur-lg p-8 rounded-lg shadow-lg max-w-3xl text-center">
        <h1 className="text-4xl font-extrabold mb-4">About iEngine</h1>
        <p className="text-lg mb-4">
          iEngine is a powerful inference engine designed for propositional logic. It allows users to upload files, select inference methods, and process logical statements efficiently.
        </p>
        <p className="text-lg mb-4">
          Developed by Truong Thien and Thanh Truc, iEngine aims to provide a user-friendly interface for logical inference and truth table generation.
        </p>
        <p className="text-lg">
          Explore the features and capabilities of iEngine to enhance your understanding of propositional logic and inference methods.
        </p>
      </div>
    </div>
  );
};

export default About;