# teaMachineVisionSystem

**teaMachineVisionSystem** is part of the **teaMachine** project that demonstrates the use of machine vision techniques for measuring and controlling the ingredient dosing process in a tea maker. It was developed as part of a master's thesis to explore alternatives to traditional sensor-based methods in environments where space and cost are constrained.

## Project Overview

The primary goal of the project was to evaluate whether machine vision can effectively replace or complement conventional sensors, such as flow meters or weight scales, in a tea maker. By leveraging visual processing, the system aims to reduce the reliance on physical sensors while adding capabilities like cup detection and liquid color verification.

Key features include:
- **Liquid Dosing**: Measurement of various liquids (tea, milk, syrup) using vision-based flow detection.
- **Granulate Dosing**: Counting solid ingredients like dried fruits using object detection.
- **Cup Detection**: Identification of a cup's presence and estimation of its size using simple image processing or neural networks.
- **Color Analysis**: Determining the intensity of brewed tea to ensure quality.

## Implementation

- **Hardware**: The tea maker is equipped with a camera and standard processing hardware. No specialized industrial sensors were used to maintain cost efficiency.
- **Software**: The system utilizes OpenCV for image processing tasks like edge detection, segmentation, and object tracking. A neural network was optionally used for cup detection.
- **Testing**: Extensive experiments were conducted to compare the vision-based measurements to traditional methods. Results showed that errors of up to 30% were acceptable for the non-critical application of tea brewing.

## Key Results

- Vision-based systems successfully measured liquids and solids with reasonable accuracy for this application.
- Additional functionalities, like detecting cup presence and estimating volume, were implemented as proofs of concept.
- Challenges included handling variable lighting conditions, camera placement, and the reliability of experimental setups.

## Future Work

The project highlights the potential of integrating machine vision into small appliances. Future development could focus on:
- Enhancing the robustness of algorithms under diverse lighting conditions.
- Standardizing the test environment (e.g., fixed lighting and calibration backgrounds).
- Optimizing software to reduce computational load and improve real-time performance.
