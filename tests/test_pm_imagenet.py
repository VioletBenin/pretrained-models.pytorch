import pytest
import torch
import torch.nn as nn
from torch.autograd import Variable
import pretrainedmodels as pm
import pretrainedmodels.utils as utils

pm_args = []
for model_name in pm.model_names:
    for pretrained in pm.pretrained_settings[model_name]:
        if pretrained in ['imagenet', 'imagenet+5k']:
            pm_args.append((model_name, pretrained))

img = utils.LoadImage()('data/cat.jpg')


def equal(x,y):
    return torch.le(torch.dist(x, y), 1e-8)

@pytest.mark.parametrize('model_name, pretrained', pm_args)
def test_pm_imagenet(model_name, pretrained):
    print('test_pm_imagenet("{}")'.format(model_name))
    net = pm.__dict__[model_name](
        num_classes=1000,
        pretrained=pretrained)
    net.eval()

    if 'nasnetalarge' == model_name:
        # nasnetalarge too big for travis
        return

    if 'pnasnet5large' == model_name:
        # pnasnet5large too big for travis
        return

    tensor = utils.TransformImage(net)(img)
    tensor = tensor.unsqueeze(0)
    x = Variable(tensor, requires_grad=False)

    out_logits = net(x)
    if 'squeezenet' in model_name:
        # Conv2d without view at the end
        assert out_logits.shape == torch.Size([1,1000,1,1])
        return

    assert out_logits.shape == torch.Size([1,1000])

    out_feats = net.features(x)
    out_logits_2 = net.logits(out_feats)
    assert equal(out_logits, out_logits_2)

    if 'dpn' in model_name:
        # Conv2d instead of Linear
        return
    net.last_linear = nn.Linear(
        net.last_linear.in_features,
        10)

    out_logits_3 = net.logits(out_feats)
    assert out_logits_3.shape == torch.Size([1,10])
