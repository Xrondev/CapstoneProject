import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from tqdm import tqdm
import os


load_ckpt_flag = False

# Load the data from the npz file
data = np.load('../../../data/price_data.npz')
X_train = data['X_train']
y_train = data['y_train']
X_val = data['X_val']
y_val = data['y_val']
X_test = data['X_test']
y_test = data['y_test']

# Verify shapes
print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)
print("X_val shape:", X_val.shape)
print("y_val shape:", y_val.shape)
print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)

# Ensure there are no NaNs
X_train = np.nan_to_num(X_train)
y_train = np.nan_to_num(y_train)
X_val = np.nan_to_num(X_val)
y_val = np.nan_to_num(y_val)
X_test = np.nan_to_num(X_test)
y_test = np.nan_to_num(y_test)

# Check for GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# Define the Transformer model
class CustomTimeSeriesTransformer(nn.Module):
    def __init__(self, input_dim, embed_dim, num_heads, num_layers, ff_dim, dropout=0.1):
        super(CustomTimeSeriesTransformer, self).__init__()
        self.embedding = nn.Linear(input_dim, embed_dim)
        self.positional_encoding = nn.Parameter(torch.zeros(1, 5000, embed_dim))  # Adjustable max sequence length
        self.encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=num_heads, dim_feedforward=ff_dim,
                                                        dropout=dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(embed_dim, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src):
        src_embedded = self.embedding(src) + self.positional_encoding[:, :src.size(1), :]
        src_embedded = self.dropout(src_embedded)
        memory = self.transformer_encoder(src_embedded)
        out = self.fc_out(memory[:, -1, :])  # Use the last time step's output
        return out


# Define model hyperparameters
input_dim = X_train.shape[2]
embed_dim = 64
num_heads = 8
num_layers = 3
ff_dim = 256  # Feedforward network dimension
dropout = 0.1


# Function to save checkpoint
def save_checkpoint(state, filename="checkpoint.pth.tar"):
    print("=> Saving checkpoint")
    torch.save(state, filename)


# Function to load checkpoint
def load_checkpoint(checkpoint, model, optimizer):
    print("=> Loading checkpoint")
    model.load_state_dict(checkpoint['state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer'])


# Initialize the model and optimizer
model = CustomTimeSeriesTransformer(input_dim, embed_dim, num_heads, num_layers, ff_dim, dropout).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.0001)

# Load checkpoint if exists
checkpoint_path = "checkpoint.pth.tar"
if os.path.isfile(checkpoint_path) and load_ckpt_flag:
    checkpoint = torch.load(checkpoint_path)
    load_checkpoint(checkpoint, model, optimizer)
    start_epoch = checkpoint['epoch'] + 1
    train_losses = checkpoint['train_losses']
else:
    start_epoch = 0
    train_losses = []


# Apply weight initialization
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_normal_(m.weight)
        nn.init.zeros_(m.bias)


model.apply(init_weights)

criterion = nn.MSELoss()

# Create DataLoader for training
train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32).to(device),
                              torch.tensor(y_train, dtype=torch.float32).unsqueeze(1).to(device))
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Training loop with loss storage, progress bar, and checkpointing
num_epochs = 5

for epoch in range(start_epoch, num_epochs):
    model.train()
    epoch_loss = 0
    progress_bar = tqdm(train_loader, desc=f'Epoch {epoch + 1}/{num_epochs}', unit='batch')
    for src, trg in progress_bar:
        optimizer.zero_grad()
        output = model(src)  # Use only src for the encoder
        loss = criterion(output, trg)
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()
        epoch_loss += loss.item()
        progress_bar.set_postfix(loss=loss.item())

    epoch_loss /= len(train_loader)
    train_losses.append(epoch_loss)
    print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {epoch_loss:.4f}')

    # Save checkpoint
    checkpoint = {
        'epoch': epoch,
        'state_dict': model.state_dict(),
        'optimizer': optimizer.state_dict(),
        'train_losses': train_losses
    }
    save_checkpoint(checkpoint, filename=checkpoint_path)

# Plot training loss
plt.figure(figsize=(10, 6))
plt.plot(train_losses, label='Training Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss Over Epochs')
plt.legend()
plt.show()


# Function to make predictions
def predict(model, src):
    model.eval()
    with torch.no_grad():
        prediction = model(src)  # Use only src for the encoder
    return prediction


# Move test data to GPU
X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1).to(device)

# Make predictions on the test set
predictions = predict(model, X_test_tensor)

# Convert predictions and actual values to numpy arrays
predictions_np = predictions.cpu().numpy().flatten()
y_test_np = y_test_tensor.cpu().numpy().flatten()

# Plot actual vs predicted values
plt.figure(figsize=(14, 7))
plt.plot(y_test_np, label='Actual', alpha=0.7)
plt.plot(predictions_np, label='Predicted', alpha=0.7)
plt.xlabel('Time Step')
plt.ylabel('Close Price')
plt.title('Actual vs Predicted Close Prices')
plt.legend()
plt.show()
