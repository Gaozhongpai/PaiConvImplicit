import torch
import copy
from tqdm import tqdm
import numpy as np
from psbody.mesh import Mesh

def test_autoencoder_dataloader(device, model, dataloader_test, shapedata, mm_constant = 1000):
    model.eval()
    l1_loss = 0
    l2_loss = 0
    shapedata_mean = torch.Tensor(shapedata.mean).to(device)
    shapedata_std = torch.Tensor(shapedata.std).to(device)
    template = Mesh(filename='./mesh_head/head_high1.obj')
    with torch.no_grad():
        for i, tx in enumerate(tqdm(dataloader_test)):
            coords, bcoords, trilist, first_idx, index_sub = dataloader_test.dataset.random_submesh()

            verts_init = []
            for name in dataloader_test.dataset.name:
                verts_init.append(tx[:, index_sub[name]])
            verts_init = torch.cat(verts_init, dim=1)

            tx, verts_init, coords, bcoords, trilist, first_idx = \
                tx.to(device), verts_init.to(device), coords.to(device), \
                bcoords.to(device), trilist.to(device), first_idx.to(device)
            prediction = model(verts_init, coords, bcoords, trilist, first_idx)
            
            verts_init = prediction[0].cpu().numpy()
            verts_init[np.where(np.isnan(verts_init))]=0.0

            template.v = verts_init
            template.write_obj('./images/test.obj')
            # prediction = model(tx)  
            if i==0:
                predictions = copy.deepcopy(prediction)
            else:
                predictions = torch.cat([predictions,prediction],0) 
            
            # l1_loss+= torch.mean(torch.abs(x_recon-x))*x.shape[0]/float(len(dataloader_test.dataset))
            
            # x_recon = (x_recon * shapedata_std + shapedata_mean) * mm_constant
            # x = (x * shapedata_std + shapedata_mean) * mm_constant
            # l2_loss+= torch.mean(torch.sqrt(torch.sum((x_recon - x)**2,dim=2)))*x.shape[0]/float(len(dataloader_test.dataset))
            
        predictions = predictions.cpu()
        # l1_loss = l1_loss.item()
        # l2_loss = l2_loss.item()
    
    return predictions # , l1_loss.cpu(), l2_loss.cpu()