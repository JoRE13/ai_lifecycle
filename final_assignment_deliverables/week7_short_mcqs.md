Q1: Which failure mode is best described by a model whose training loss never decreases meaningfully?

a) The model does not learn because optimization is broken.

b) The model works offline but fails in production.

c) The model generalizes poorly because variance is too low.

d) The model is miscalibrated despite high validation accuracy.

Correct Answer: a) The model does not learn because optimization is broken.

Q2: Which failure mode is most directly associated with a model that performs well on validation data but poorly after deployment because user behavior changed?

a) Exploding gradients.

b) Distribution shift.

c) Symmetry breaking.

d) Gradient accumulation.

Correct Answer: b) Distribution shift.

Q3: For spreadsheet or tabular data, which model family is commonly a strong baseline and often competitive with neural networks?

a) State space models.

b) Visual transformers.

c) Gradient boosting.

d) Convolutional filters.

Correct Answer: c) Gradient boosting.

Q4: For image data, which pair of architectures is identified as a top choice in the slides?

a) Naive Bayes and decision stumps.

b) RNNs and state space models.

c) Linear models and autoencoders.

d) CNNs and visual transformers.

Correct Answer: d) CNNs and visual transformers.

Q5: For text processing, which architecture family currently dominates most state-of-the-art systems?

a) Transformers.

b) Convolutional neural networks.

c) Random forests.

d) Gaussian processes.

Correct Answer: a) Transformers.

Q6: Why should pre-trained models be used whenever possible?

a) They remove the need for validation data.

b) They save time and computational resources.

c) They guarantee perfect calibration.

d) They eliminate all distribution shift.

Correct Answer: b) They save time and computational resources.

Q7: What is the central purpose of self-attention in a transformer?

a) It forces each layer to use fixed-size convolutional filters.

b) It normalizes every feature across the training batch.

c) It lets each input part interact with other input parts.

d) It averages all model predictions into one ensemble.

Correct Answer: c) It lets each input part interact with other input parts.

Q8: Which components are combined in transformer blocks to support stable deep learning?

a) Tokenization, label smoothing, imputation, and one-hot encoding.

b) Boosted trees, feature hashing, pruning, and majority voting.

c) Bagging, resampling, calibration, and isotonic regression.

d) Self-attention, feed-forward layers, residual connections, and normalization.

Correct Answer: d) Self-attention, feed-forward layers, residual connections, and normalization.

Q9: Why is LayerNorm especially suitable for transformers?

a) It normalizes each sample across its features.

b) It depends strongly on large batch statistics.

c) It replaces attention with convolutional kernels.

d) It averages gradients across multiple devices.

Correct Answer: a) It normalizes each sample across its features.

Q10: When is BatchNorm generally a good default?

a) For transformer models with variable sequence lengths.

b) For vision CNNs trained with reasonably large batches.

c) For style transfer models with single-image batches.

d) For calibration models trained on holdout logits.

Correct Answer: b) For vision CNNs trained with reasonably large batches.

Q11: What distinguishes RMSNorm from LayerNorm?

a) RMSNorm normalizes over the batch dimension only.

b) RMSNorm trains a combiner model on base model outputs.

c) RMSNorm skips mean subtraction and divides by root mean square.

d) RMSNorm applies decoupled weight decay to parameters.

Correct Answer: c) RMSNorm skips mean subtraction and divides by root mean square.

Q12: Which normalization method is especially associated with style transfer and image generation?

a) BatchNorm.

b) LayerNorm.

c) RMSNorm.

d) InstanceNorm.

Correct Answer: d) InstanceNorm.

Q13: Which normalization method is useful for small-batch vision tasks such as detection or segmentation?

a) GroupNorm.

b) BatchNorm.

c) Platt scaling.

d) Softmax normalization.

Correct Answer: a) GroupNorm.

Q14: Which sequence best describes the deep learning training loop?

a) Choose optimizer, skip validation, deploy, calibrate, freeze, repeat.

b) Choose metric, choose loss, train, validate, analyze errors, adjust, repeat.

c) Choose labels, average models, remove training data, deploy, repeat.

d) Choose hardware, compress labels, increase batch size, stop, repeat.

Correct Answer: b) Choose metric, choose loss, train, validate, analyze errors, adjust, repeat.

Q15: In the training strategy example, what is the role of macro-averaged F1 score?

a) It is the optimizer used to update weights.

b) It is the initialization method for the model.

c) It is the performance metric used for evaluation.

d) It is the loss function minimized during training.

Correct Answer: c) It is the performance metric used for evaluation.

Q16: Which cost function is most appropriate for standard regression tasks?

a) Binary cross-entropy.

b) Contrastive loss.

c) Categorical cross-entropy.

d) Mean squared error.

Correct Answer: d) Mean squared error.

Q17: Which cost function is most appropriate for multiclass classification with one correct class?

a) Categorical cross-entropy.

b) Mean squared error.

c) Binary cross-entropy per label.

d) Isotonic regression loss.

Correct Answer: a) Categorical cross-entropy.

Q18: Which cost function is most appropriate for multilabel classification where one instance can belong to several classes?

a) Mean squared error.

b) Binary cross-entropy.

c) Categorical cross-entropy.

d) Cosine annealing.

Correct Answer: b) Binary cross-entropy.

Q19: Why does cross-entropy heavily penalize a confidently wrong prediction?

a) The loss ignores probabilities and only counts incorrect class labels.

b) The loss becomes small when the predicted probability for any class is high.

c) The loss becomes large when the predicted probability for the true class is low.

d) The loss averages predictions across all models in the ensemble.

Correct Answer: c) The loss becomes large when the predicted probability for the true class is low.

Q20: Two models classify a cat image as dog. Model A assigns 49% to cat, while Model B assigns 1% to cat. Which has the larger cross-entropy loss?

a) Model A, because it was less confident in dog.

b) Model B, because cross-entropy ignores true class probability.

c) Model A, because cross-entropy rewards uncertainty.

d) Model B, because it assigned lower probability to the true class.

Correct Answer: d) Model B, because it assigned lower probability to the true class.

Q21: Which output activation is appropriate for binary classification?

a) Sigmoid.

b) ReLU.

c) Linear.

d) Softmax.

Correct Answer: a) Sigmoid.

Q22: Which output activation is appropriate for multiclass classification where class probabilities must sum to one?

a) Sigmoid per label.

b) Softmax.

c) Linear.

d) Tanh.

Correct Answer: b) Softmax.

Q23: Which output activation is appropriate for multilabel classification?

a) Softmax over all labels.

b) Linear output for every label.

c) Sigmoid independently per label.

d) Tanh shared across labels.

Correct Answer: c) Sigmoid independently per label.

Q24: What is the main risk of ReLU activations?

a) They require labels to be one-hot encoded.

b) They require batch statistics at inference.

c) They force outputs to sum to one.

d) They can produce dead neurons.

Correct Answer: d) They can produce dead neurons.

Q25: Which activation is listed as a common default for transformers, BERT, GPT, and ViTs?

a) GELU.

b) ELU.

c) Tanh.

d) Linear.

Correct Answer: a) GELU.

Q26: Which activation is described as gated and used in modern LLMs such as LLaMA, Mistral, and Gemma?

a) ReLU.

b) SwiGLU.

c) Tanh.

d) Sigmoid.

Correct Answer: b) SwiGLU.

Q27: What does gradient descent do when updating parameters?

a) It moves parameters by averaging predictions from all base models.

b) It moves parameters toward the largest validation metric value directly.

c) It moves parameters in the opposite direction of the cost gradient.

d) It moves parameters by sampling only misclassified validation examples.

Correct Answer: c) It moves parameters in the opposite direction of the cost gradient.

Q28: What is a key drawback of full gradient descent on large datasets?

a) It makes noisy updates after every individual example.

b) It always diverges because gradients are too unstable.

c) It cannot compute gradients for differentiable losses.

d) It performs only one update per full pass through the data.

Correct Answer: d) It performs only one update per full pass through the data.

Q29: What is the practical tradeoff of increasing minibatch size?

a) Larger batches make fewer updates per epoch but more stable gradients.

b) Larger batches make more updates per epoch but noisier gradients.

c) Larger batches remove the need for a validation dataset.

d) Larger batches guarantee better generalization in production.

Correct Answer: a) Larger batches make fewer updates per epoch but more stable gradients.

Q30: What does gradient clipping by norm do?

a) It freezes the largest layer when validation loss increases.

b) It scales the gradient vector if its L2 norm exceeds a threshold.

c) It divides the dataset into cross-validation folds.

d) It removes low-confidence examples from the training set.

Correct Answer: b) It scales the gradient vector if its L2 norm exceeds a threshold.

Q31: What is the purpose of gradient accumulation?

a) To calibrate predictions using a non-decreasing function.

b) To reduce validation loss by training a separate combiner.

c) To simulate a larger batch size using several micro-batches.

d) To detect distribution shift with a binary classifier.

Correct Answer: c) To simulate a larger batch size using several micro-batches.

Q32: Which hyperparameter is described as often the most sensitive in deep learning training?

a) Batch size.

b) Choice of optimizer.

c) Nonlinearity choice.

d) Learning rate.

Correct Answer: d) Learning rate.

Q33: What is the purpose of learning-rate warmup?

a) To gradually increase the learning rate early and reduce instability.

b) To randomly shuffle labels before each optimization step.

c) To remove the need for a cost function during training.

d) To average model checkpoints from different architectures.

Correct Answer: a) To gradually increase the learning rate early and reduce instability.

Q34: Which learning-rate schedule is presented as the standard modern schedule for most training tasks?

a) Step decay.

b) Cosine annealing.

c) Constant rate.

d) Exponential growth.

Correct Answer: b) Cosine annealing.

Q35: Which learning-rate schedule is described as standard for large-scale LLM pretraining?

a) One-cycle policy.

b) Step-based decay.

c) Warmup-stable-decay.

d) Time-based decay.

Correct Answer: c) Warmup-stable-decay.

Q36: Which schedule ramps the learning rate from low to high and then back down in one cycle?

a) Exponential decay.

b) Step decay.

c) Warmup-stable-decay.

d) One-cycle policy.

Correct Answer: d) One-cycle policy.

Q37: What does momentum add to optimization?

a) It incorporates information from previous steps to smooth the path.

b) It normalizes every sample independently across its features.

c) It trains a binary classifier to detect train-test differences.

d) It decouples validation metrics from the training objective.

Correct Answer: a) It incorporates information from previous steps to smooth the path.

Q38: What is the core idea of RMSProp?

a) It replaces gradients with majority votes from multiple classifiers.

b) It adapts per-parameter step sizes based on recent gradient magnitudes.

c) It initializes weights using only the number of output neurons.

d) It calibrates logits by fitting a non-decreasing function.

Correct Answer: b) It adapts per-parameter step sizes based on recent gradient magnitudes.

Q39: What does Adam combine?

a) Label smoothing and isotonic regression calibration.

b) BatchNorm statistics and cross-validation fold predictions.

c) Momentum for direction and RMSProp-style adaptive step sizes.

d) Data parallelism and tensor parallelism in one layer.

Correct Answer: c) Momentum for direction and RMSProp-style adaptive step sizes.

Q40: What is the key difference between Adam and AdamW?

a) AdamW applies softmax over the wrong dimension by design.

b) AdamW removes momentum and uses only raw stochastic gradients.

c) AdamW requires all training examples to fit into one full batch.

d) AdamW applies weight decay directly to parameters, separate from the gradient update.

Correct Answer: d) AdamW applies weight decay directly to parameters, separate from the gradient update.

Q41: Why is L2 regularization not equivalent to decoupled weight decay when using Adam-style optimizers?

a) L2 in the loss is scaled by adaptive learning rates.

b) L2 in the loss removes all gradient information.

c) L2 in the loss disables bias correction entirely.

d) L2 in the loss changes the labels during training.

Correct Answer: a) L2 in the loss is scaled by adaptive learning rates.

Q42: In the slides, which optimizer is recommended as a robust default for most deep learning applications?

a) RMSProp.

b) AdamW.

c) Momentum SGD.

d) Schedule-Free.

Correct Answer: b) AdamW.

Q43: If training loss decreases steadily while validation loss starts increasing after epoch 10, what is the most likely diagnosis?

a) Vanishing gradients.

b) Data corruption.

c) Overfitting.

d) Learning rate too low.

Correct Answer: c) Overfitting.

Q44: What is a reasonable first action when validation loss rises while training loss continues to fall?

a) Replace the labels with model predictions.

b) Remove the validation set from evaluation.

c) Increase the learning rate without testing.

d) Add regularization or use early stopping.

Correct Answer: d) Add regularization or use early stopping.

Q45: What is one goal of parameter initialization?

a) To break symmetry between neurons.

b) To replace the optimizer entirely.

c) To calibrate probabilities after training.

d) To create train-test distribution shift.

Correct Answer: a) To break symmetry between neurons.

Q46: Which initialization method is recommended for sigmoid or tanh activations?

a) Kaiming initialization.

b) Xavier initialization.

c) Random label initialization.

d) Decoupled initialization.

Correct Answer: b) Xavier initialization.

Q47: Why does Kaiming initialization include a correction factor for ReLU-like activations?

a) ReLU requires a holdout calibration dataset.

b) ReLU makes every output probability sum to one.

c) ReLU discards negative activations, changing variance flow.

d) ReLU trains one model per class imbalance subset.

Correct Answer: c) ReLU discards negative activations, changing variance flow.

Q48: What happens in vanishing gradients?

a) Gradients are stored for many micro-batches before updating.

b) Gradients grow without bound and immediately improve accuracy.

c) Gradients are averaged across devices during data parallelism.

d) Gradients shrink toward zero and early layers stop learning.

Correct Answer: d) Gradients shrink toward zero and early layers stop learning.

Q49: What happens in exploding gradients?

a) Gradients become enormous and training can diverge to NaN.

b) Gradients become zero and labels are automatically corrected.

c) Gradients become calibrated probabilities after Platt scaling.

d) Gradients become validation examples for model stacking.

Correct Answer: a) Gradients become enormous and training can diverge to NaN.

Q50: According to the top-3 tuning order, what should usually be tuned first?

a) Choice of nonlinearity.

b) Learning rate and schedule.

c) Size of minibatch.

d) Optimizer properties.

Correct Answer: b) Learning rate and schedule.

Q51: What is the goal of balancing bias and variance?

a) To ensure every output activation is a softmax distribution.

b) To replace validation data with training data for faster iteration.

c) To trade off underfitting and overfitting for better generalization.

d) To force all user segments to have identical input features.

Correct Answer: c) To trade off underfitting and overfitting for better generalization.

Q52: What is the typical architecture pattern for multitask learning?

a) A calibration model trained before the base model.

b) One independent model for every training example.

c) A single output head with no shared representation.

d) A shared encoder with task-specific heads.

Correct Answer: d) A shared encoder with task-specific heads.

Q53: What is negative transfer in multitask learning?

a) Unrelated tasks hurt shared model performance.

b) Related tasks improve effective sample size.

c) Calibration data makes probabilities conservative.

d) Batch statistics become noisy in small batches.

Correct Answer: a) Unrelated tasks hurt shared model performance.

Q54: What is the basic idea of transfer learning?

a) Train a model from scratch whenever data is limited.

b) Use a pre-trained model from a related task as a starting point.

c) Replace the optimizer with a data validation classifier.

d) Combine models only by majority voting.

Correct Answer: b) Use a pre-trained model from a related task as a starting point.

Q55: For 500 labeled chest X-rays, which strategy is ranked best in the slides?

a) Train a CNN from scratch on the 500 images.

b) Fine-tune an ImageNet-pretrained ResNet only.

c) Apply LoRA to a medical imaging foundation model.

d) Use a linear model on raw pixel intensities.

Correct Answer: c) Apply LoRA to a medical imaging foundation model.

Q56: When is full fine-tuning most appropriate for a 7B model?

a) When calibration is the only training objective.

b) When only one consumer GPU is available.

c) When no labeled examples are available.

d) When maximum quality is needed and compute is abundant.

Correct Answer: d) When maximum quality is needed and compute is abundant.

Q57: When is QLoRA especially useful?

a) When prototyping on a single consumer GPU.

b) When training a model from scratch on unlimited GPUs.

c) When replacing cross-entropy with mean squared error.

d) When detecting train-test shift without labels.

Correct Answer: a) When prototyping on a single consumer GPU.

Q58: In LoRA, what does the rank control?

a) The number of validation folds used in stacking.

b) The capacity and efficiency tradeoff of the adapter.

c) The probability threshold used for calibration.

d) The exact number of classes in softmax.

Correct Answer: b) The capacity and efficiency tradeoff of the adapter.

Q59: What is ensemble learning?

a) Calibrating one model with a holdout validation set.

b) Freezing a single model to reduce its training time.

c) Combining multiple models to improve accuracy and robustness.

d) Initializing one model with variance-preserving weights.

Correct Answer: c) Combining multiple models to improve accuracy and robustness.

Q60: Which ensemble method is best suited to combining several regression models with similar performance?

a) Majority voting.

b) Group normalization.

c) Platt scaling.

d) Averaging.

Correct Answer: d) Averaging.

Q61: Which ensemble method is best suited to combining several classifiers by class decision?

a) Majority voting.

b) Gradient clipping.

c) Instance normalization.

d) Warmup scheduling.

Correct Answer: a) Majority voting.

Q62: What does model stacking train?

a) A calibration curve that must always be sigmoid-shaped.

b) A combiner model that uses base model outputs as inputs.

c) A batch-normalized layer that averages feature maps.

d) A data-parallel replica that owns one part of the batch.

Correct Answer: b) A combiner model that uses base model outputs as inputs.

Q63: How can stacking avoid data leakage when training the combiner?

a) Remove the validation set and train all models on the same examples.

b) Train the combiner on base model predictions for their own training rows.

c) Use out-of-fold base model predictions to train the combiner.

d) Calibrate each base model only after deployment begins.

Correct Answer: c) Use out-of-fold base model predictions to train the combiner.

Q64: How can ensembling address an imbalanced dataset?

a) Increase the learning rate until minority examples dominate gradients.

b) Remove the minority class so every base model sees balanced labels.

c) Train only on majority examples and calibrate probabilities afterward.

d) Partition the majority class into subsets and include minority data with each base model.

Correct Answer: d) Partition the majority class into subsets and include minority data with each base model.

Q65: What is distribution shift?

a) A change in data distribution over time or environment that hurts performance.

b) A reduction in model parameters caused by weight decay.

c) A normalization method that divides activations by root mean square.

d) A calibration method that fits logistic regression to logits.

Correct Answer: a) A change in data distribution over time or environment that hurts performance.

Q66: Which type of shift occurs when the distribution of input features changes?

a) Prior probability shift.

b) Covariate shift.

c) Concept drift.

d) Calibration shift.

Correct Answer: b) Covariate shift.

Q67: Which type of shift occurs when the distribution of the target variable changes?

a) Covariate shift.

b) Concept drift.

c) Prior probability shift.

d) Gradient shift.

Correct Answer: c) Prior probability shift.

Q68: Which type of shift occurs when the relationship between inputs and targets changes?

a) Covariate shift.

b) Prior probability shift.

c) Weight decay.

d) Concept drift.

Correct Answer: d) Concept drift.

Q69: What is adversarial validation used for?

a) Detecting train-test distribution shift with a binary classifier.

b) Updating parameters by moving opposite the cost gradient.

c) Combining regression predictions with simple averaging.

d) Preventing dead neurons by changing activation functions.

Correct Answer: a) Detecting train-test distribution shift with a binary classifier.

Q70: What does high accuracy in an adversarial validation classifier suggest?

a) The model is perfectly calibrated.

b) Train and test examples are easy to distinguish.

c) The optimizer has reached the global optimum.

d) The validation labels contain no mistakes.

Correct Answer: b) Train and test examples are easy to distinguish.

Q71: When is probability calibration especially important?

a) When labels are removed before training.

b) When only the top-ranked class matters.

c) When decisions depend on probability magnitude.

d) When outputs are never used for decisions.

Correct Answer: c) When decisions depend on probability magnitude.

Q72: What does it mean for a model to be well calibrated?

a) The model reaches 100% accuracy on a tiny minibatch.

b) Every class receives exactly the same predicted probability.

c) The validation loss is always lower than the training loss.

d) Events predicted at 70% probability occur about 70% of the time.

Correct Answer: d) Events predicted at 70% probability occur about 70% of the time.

Q73: Which calibration technique fits logistic regression to model outputs?

a) Platt scaling.

b) Isotonic regression.

c) Gradient accumulation.

d) Cosine annealing.

Correct Answer: a) Platt scaling.

Q74: Which calibration technique fits a non-decreasing function and usually needs more calibration data?

a) Platt scaling.

b) Isotonic regression.

c) Batch normalization.

d) Majority voting.

Correct Answer: b) Isotonic regression.

Q75: In a reliability diagram, what does a curve above the diagonal indicate?

a) The model is perfectly calibrated because all points lie on the diagonal.

b) The model is over-confident because predicted probability exceeds actual frequency.

c) The model is under-confident because actual frequency exceeds predicted probability.

d) The model has distribution shift because inputs are easy to distinguish.

Correct Answer: c) The model is under-confident because actual frequency exceeds predicted probability.

Q76: What is the purpose of systematic error analysis?

a) To avoid inspecting mislabeled examples manually.

b) To replace all validation metrics with training loss.

c) To guarantee that distribution shift cannot occur.

d) To identify specific error patterns and guide targeted fixes.

Correct Answer: d) To identify specific error patterns and guide targeted fixes.

Q77: In the dog-breed classifier example, which action directly addresses blurry or low-resolution photos?

a) Add blur augmentation.

b) Apply Platt scaling.

c) Increase LoRA rank.

d) Use majority voting.

Correct Answer: a) Add blur augmentation.

Q78: What is a focused classification error?

a) A uniformly random error pattern across all examples.

b) An error pattern concentrated in specific groups of examples.

c) A numerical problem caused only by FP16 precision.

d) A calibration issue where all classes sum to one.

Correct Answer: b) An error pattern concentrated in specific groups of examples.

Q79: Which technique can help visually inspect clusters of misclassified examples?

a) BF16 or FP8.

b) AdamW or RMSProp.

c) PCA or UMAP.

d) Xavier or Kaiming.

Correct Answer: c) PCA or UMAP.

Q80: Why simulate ideal outcomes for components in a complex ML system?

a) To force the final model to use a single multiclass softmax head.

b) To remove the need for monitoring distribution shift after deployment.

c) To make every component use the same optimizer and learning rate.

d) To identify which component improvement would yield the biggest overall gain.

Correct Answer: d) To identify which component improvement would yield the biggest overall gain.

Q81: How should validation performance be checked across user segments?

a) Divide the validation set by segment and inspect disparities.

b) Train only on the largest user segment and ignore smaller groups.

c) Remove segment labels because they can reveal focused errors.

d) Replace per-segment validation with one training loss curve.

Correct Answer: a) Divide the validation set by segment and inspect disparities.

Q82: What is a recommended way to handle suspected bad labels?

a) Increase model depth until the labels become consistent.

b) Review mismatches or near-threshold cases with annotator agreement.

c) Use a larger batch size to average away label errors.

d) Apply softmax twice before computing cross-entropy.

Correct Answer: b) Review mismatches or near-threshold cases with annotator agreement.

Q83: What is Cleanlab used for in the slides?

a) Applying decoupled weight decay to model parameters.

b) Sharding optimizer states across multiple GPUs.

c) Detecting and correcting label errors automatically.

d) Replacing cross-validation in model stacking.

Correct Answer: c) Detecting and correcting label errors automatically.

Q84: In active learning, why prioritize points near the decision threshold?

a) They remove the need for labeled validation examples.

b) They are always correctly labeled and require no review.

c) They guarantee the lowest cross-entropy in the dataset.

d) They are uncertain and often provide high information gain.

Correct Answer: d) They are uncertain and often provide high information gain.

Q85: Why should you try to overfit a tiny batch during training setup?

a) To confirm that the model, loss, labels, and optimizer can learn at all.

b) To prove that the model will generalize after production deployment.

c) To make the validation loss higher than the training loss permanently.

d) To replace hyperparameter tuning with a single deterministic result.

Correct Answer: a) To confirm that the model, loss, labels, and optimizer can learn at all.

Q86: If error goes up when trying to overfit a minibatch, which issue is plausible?

a) Too much distribution monitoring.

b) Incorrect sign on the cost function.

c) Excessive calibration data.

d) Too many validation segments.

Correct Answer: b) Incorrect sign on the cost function.

Q87: If error explodes upward when trying to overfit a minibatch, which issue is plausible?

a) Labels are already calibrated.

b) Batch size is perfectly tuned.

c) Learning rate is too high.

d) Model stacking is leakage-free.

Correct Answer: c) Learning rate is too high.

Q88: If error oscillates wildly and learning rate is reasonable, what should be checked first?

a) Whether logits should be averaged across all classes.

b) Whether cosine annealing should be replaced by WSD.

c) Whether GroupNorm should become InstanceNorm.

d) Whether data or labels are corrupted or shuffled.

Correct Answer: d) Whether data or labels are corrupted or shuffled.

Q89: If error plateaus while trying to overfit a minibatch, which cause is plausible?

a) Learning rate is too low.

b) Confidence scores are too calibrated.

c) Training data is too recent.

d) The model has too many checkpoints.

Correct Answer: a) Learning rate is too low.

Q90: After successfully overfitting a minibatch, what is the next major training step?

a) Remove all validation examples and deploy the model immediately.

b) Train on the full dataset and monitor training and validation curves.

c) Freeze the model and only tune calibration on production data.

d) Replace the architecture with an unrelated larger model automatically.

Correct Answer: b) Train on the full dataset and monitor training and validation curves.

Q91: What is a correction cascade?

a) A model is replicated on several GPUs and gradients are averaged.

b) A learning-rate schedule decays smoothly using a cosine function.

c) A model B is built to correct outputs from model A, creating hidden dependencies.

d) A calibration curve lies above the diagonal reliability line.

Correct Answer: c) A model B is built to correct outputs from model A, creating hidden dependencies.

Q92: What is the recommended alternative to a correction cascade?

a) Ignore updates to model A once model B is deployed.

b) Add more correction models after every deployment.

c) Train model B only on validation predictions from model A.

d) Fix model A directly or build an independent model.

Correct Answer: d) Fix model A directly or build an independent model.

Q93: Which practice supports reproducibility?

a) Fix random seeds and document hyperparameters and infrastructure.

b) Change labels after every epoch without recording the changes.

c) Use undocumented defaults and avoid experiment tracking.

d) Delete failed runs before comparing validation metrics.

Correct Answer: a) Fix random seeds and document hyperparameters and infrastructure.

Q94: What should experiment tracking record for deep learning runs?

a) Only the final test accuracy and the deployed model filename.

b) Hyperparameters, loss curves, gradient norms, checkpoints, schedules, and validation metrics.

c) Only the optimizer name and the largest training batch.

d) Only the number of labels and the random seed value.

Correct Answer: b) Hyperparameters, loss curves, gradient norms, checkpoints, schedules, and validation metrics.

Q95: Why is BF16 preferred for modern mixed precision training?

a) It guarantees higher accuracy than full FP32 in every setting.

b) It removes the need for master weights during optimization.

c) It has FP32-like dynamic range with about half the memory use.

d) It forces every operation to run on the CPU instead of GPU.

Correct Answer: c) It has FP32-like dynamic range with about half the memory use.

Q96: What is the common mixed precision workflow described in the slides?

a) Keep logits in FP8 and avoid backpropagation entirely.

b) Keep master weights in INT8 and run all validation in FP64.

c) Keep labels in BF16 and run the optimizer with no gradients.

d) Keep master weights in FP32 and run forward/backward passes in BF16.

Correct Answer: d) Keep master weights in FP32 and run forward/backward passes in BF16.

Q97: What is data parallelism?

a) Replicate the model on multiple GPUs, split batches, and average gradients.

b) Split each layer matrix across GPUs using high-bandwidth interconnects.

c) Split model layers sequentially across GPUs using micro-batches.

d) Shard parameters, gradients, and optimizer states across GPUs.

Correct Answer: a) Replicate the model on multiple GPUs, split batches, and average gradients.

Q98: What is pipeline parallelism?

a) Split each matrix multiplication across GPUs at the tensor level.

b) Split model layers across GPUs and use micro-batching to keep them busy.

c) Replicate the full model on every GPU and average gradients.

d) Calibrate each GPU output with isotonic regression.

Correct Answer: b) Split model layers across GPUs and use micro-batching to keep them busy.

Q99: What is tensor parallelism?

a) Split validation examples into user segments for error analysis.

b) Split the training set into cross-validation blocks for model stacking.

c) Split individual layers, such as large matrix multiplications, across GPUs.

d) Split classes into majority and minority subsets for ensembling.

Correct Answer: c) Split individual layers, such as large matrix multiplications, across GPUs.

Q100: What does PyTorch FSDP do?

a) Uses out-of-fold predictions to train a stacking combiner.

b) Fits logistic regression to model outputs for calibration.

c) Applies sigmoid independently to every multilabel output.

d) Shards parameters, gradients, and optimizer states across GPUs.

Correct Answer: d) Shards parameters, gradients, and optimizer states across GPUs.

Q101: When do distributed training techniques become most relevant?

a) When models exceed about 1B parameters or cannot fit on one GPU.

b) When a model has only a few thousand parameters and trains instantly.

c) When validation accuracy is perfect on every user segment.

d) When a tabular model is small enough for CPU-only inference.

Correct Answer: a) When models exceed about 1B parameters or cannot fit on one GPU.

Q102: Which item belongs in the end-to-end training checklist before full training?

a) Deploy the model before checking whether labels are correct.

b) Run pipeline sanity checks for shapes, labels, and data loading.

c) Tune calibration before selecting a metric or loss function.

d) Ignore tiny-batch overfitting because it encourages memorization.

Correct Answer: b) Run pipeline sanity checks for shapes, labels, and data loading.

Q103: Which item belongs near the end of the training checklist for production systems?

a) Disable validation metric tracking.

b) Remove all experiment tracking logs.

c) Set up distribution shift monitoring.

d) Train only on a single tiny batch.

Correct Answer: c) Set up distribution shift monitoring.

Q104: In the training checklist, when should calibration be prioritized?

a) When labels are unavailable.

b) When only class ranking matters.

c) When outputs are never inspected.

d) When probabilities drive decisions.

Correct Answer: d) When probabilities drive decisions.