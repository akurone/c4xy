import os
import random
import numpy as np

from transformers import DecisionTransformerModel
import torch

def seed_everything(seed: int = 42, deterministic: bool = True):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(deterministic)
    os.environ['PYTHONHASHSEED'] = str(seed)

class TrainableDT(DecisionTransformerModel):
    def __init__(self, config):
        super().__init__(config)

    def forward(self, **kwargs):
        output = super().forward(**kwargs)
        # add the DT loss
        action_preds = output[1]
        action_targets = kwargs["actions"]
        attention_mask = kwargs["attention_mask"]
        act_dim = action_preds.shape[2]
        action_preds = action_preds.reshape(-1, act_dim)[attention_mask.reshape(-1) > 0]
        action_targets = action_targets.reshape(-1, act_dim)[attention_mask.reshape(-1) > 0]
        
        # Use Cross Entropy Loss
        criterion = torch.nn.CrossEntropyLoss()
        loss = criterion(action_preds, action_targets)

        return {"loss": loss}

    def original_forward(self, **kwargs):
        return super().forward(**kwargs)[1]
