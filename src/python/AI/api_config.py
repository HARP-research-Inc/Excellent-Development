import openai
from transformers import pipeline
import torch
from torch import nn
import importlib.util


def setup_openai(api_key):
    openai.api_key = api_key
    return openai

def setup_huggingface(model_name):
    hf_model = pipeline('text-generation', model=model_name)
    return hf_model

def import_model(module_path, class_name):
    spec = importlib.util.spec_from_file_location(class_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model_class = getattr(module, class_name)
    return model_class

def setup_local_model(model_path, model_class_path, model_class_name):
    ModelClass = import_model(model_class_path, model_class_name)
    local_model = ModelClass()
    local_model.load_state_dict(torch.load(model_path))
    return local_model

def get_model(service, identifier, model_class_path=None, model_class_name=None):
    if service.lower() == "openai":
        return setup_openai(identifier)
    elif service.lower() == "huggingface":
        return setup_huggingface(identifier)
    elif service.lower() == "local":
        if model_class_path is None or model_class_name is None:
            raise ValueError("For local model, both model_class_path and model_class_name must be provided.")
        return setup_local_model(identifier, model_class_path, model_class_name)
    else:
        raise ValueError("Invalid service. Please choose from 'openai', 'huggingface', or 'local'.")
