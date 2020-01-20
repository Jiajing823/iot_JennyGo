import pickle
import numpy as np
def clear():
    '''
    Clear the history
    '''
    d_res = {'history':{'tree': 0, 'stop': 0, 'turn': 0, 'over': 0, 'play': 0, 'go': 0, 'stone': 0}}
    d_pers = {'personality':'Mysterious'}
    d_mood = {'mood':{'flat': 0, 'excited': 0, 'tired': 0, 'worry': 0, 'think good': 0, 'think bad': 0}}
    d_current_pred = {'current': -1}
    d_mood_link = {'mood_link':{'tree': {'think bad':1}, 'stop': {'tired':1}, 'turn': {'excited':1}, 'over': {'worry':1}, 'play': {'excited':5}, 'go': {'flat':1}, 'stone': {'think good':1}}}
    predictions = dict(d_current_pred, **d_res)
    predictions = dict(predictions, **d_pers)
    predictions = dict(predictions, **d_mood)
    predictions = dict(predictions, **d_mood_link)

    print(predictions)
    f = open('predictions.pkl', 'wb')
    pickle.dump(predictions,f)
    f.close()
    
def restore():
    '''
    Restore to one specific status
    '''
    predictions = {'current': 'over', 'history': {'tree': 299, 'stop': 207, 'turn': 0, 'over': 28, 'play': 26, 'go': 73, 'stone': 222}, 'personality': 'Thoughtful', 'mood': {'flat': 0, 'excited': 0, 'tired': 0, 'worry': 1, 'think good': 0, 'think bad': 0}, 'mood_link': {'tree': {'think bad': 1}, 'stop': {'tired': 1}, 'turn': {'excited': 1}, 'over': {'worry': 1}, 'play': {'excited': 5}, 'go': {'flat': 1}, 'stone': {'think good': 1}}}
    print(predictions)
    f = open('predictions.pkl', 'wb')
    pickle.dump(predictions,f)
    f.close()
    
def check():
    '''
    Check the current status
    '''
    f = open('predictions.pkl', 'rb')
    predictions = pickle.load(f)
    f.close()
    print(predictions)
    
def judge(pred):
    '''
    Give judgement on mood and personality based on current classfication result and previous records.
    '''
    #settings
    max_count_mood = 2
    discount_factor = 0.5
    f = open('predictions.pkl', 'rb')
    predictions = pickle.load(f)
    f.close()
    new_pred = {'current': pred}
    predictions.update(new_pred)
    predictions['history'][pred] = predictions['history'][pred] + 1
    mood_pair = predictions['mood_link'][pred]
    for key, value in mood_pair.items():
        predictions['mood'][key] = predictions['mood'][key] + value
    
    res_mood = list(predictions['mood'].keys())[np.argmax([value for value in predictions['mood'].values()])]
    if (np.max([value for value in predictions['mood'].values()]) > max_count_mood):
        new_dict = {'flat': 0, 'excited': 0, 'tired': 0, 'worry': 0, 'think good': 0, 'think bad': 0}
        predictions['mood'].update(new_dict)
        predictions['mood'][res_mood] = int(max_count_mood * discount_factor)
    res_pers = predictions['personality']
    if ((predictions['history']['go'] + predictions['history']['play'] + predictions['history']['turn'] + predictions['history']['over']) 
        - (predictions['history']['stop'] + predictions['history']['stone'] + predictions['history']['tree'])) > 200:
        res_pers = 'Outgoing'
        predictions['personality'] = res_pers
    if (predictions['history']['over'] > 30) or (((predictions['history']['turn'] + predictions['history']['play'])
     - (predictions['history']['go'] + predictions['history']['stop'] + predictions['history']['stone'] + predictions['history']['tree'])) > 50):
        res_pers = 'Childish'
        predictions['personality'] = res_pers
    if (((predictions['history']['stop'] + predictions['history']['stone'] + predictions['history']['tree']) 
        - (predictions['history']['go'] + predictions['history']['play'] + predictions['history']['turn'] + predictions['history']['over']) 
        )> 200) and (predictions['history']['stop'] - predictions['history']['stone'] - predictions['history']['tree'] > 100):
        res_pers = 'Lazy'
        predictions['personality'] = res_pers
    if ((predictions['history']['stone'] + predictions['history']['tree']) 
        - (predictions['history']['go'] + predictions['history']['stop'] + predictions['history']['turn'] + predictions['history']['over'] + predictions['history']['play'])) > 200:
        res_pers = 'Thoughtful'
        predictions['personality'] = res_pers
        
    f = open('predictions.pkl', 'wb')
    pickle.dump(predictions,f)
    f.close()