from multipledispatch import dispatch

from django.forms.models import model_to_dict

from savor.base.models import Channel, UnitSale


@dispatch(str, dict)
def channel(channel_id, qstring):
    channel = Channel.objects.get(counterparty_id=channel_id)
    data = {'id': channel.id, 'counterparty_id': channel.counterparty.id}
    return data

# how to take str or unicode??
@dispatch(unicode, dict)
def channel(channel_id, qstring):
    channel = Channel.objects.get(counterparty_id=channel_id)
    data = {'id': channel.id, 'counterparty_id': channel.counterparty.id}
    return data


@dispatch(dict)
def channel(qstring):
    channels = Channel.objects.all()

    data = [{'id': channel.id, 'counterparty_id': channel.counterparty.id} for channel in channels]
    return data
