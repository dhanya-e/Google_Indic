import os
import fnmatch
import random
import re
import string
import sys

#data_dir = '/home/dhanya/PhD/Datasets/Google_Indic/kn/'
#uttid_dir = './data/local/data/'

if len(sys.argv) != 3:
    print("Usage: python data_prep.py [data_dir] [uttid_dir]")
    sys.exit(1)
data_dir = sys.argv[1]
uttid_dir = sys.argv[2]

# Create the output folder
try:
    os.stat(uttid_dir)
except:
    os.makedirs(uttid_dir)
    
print("Utt_id generation")
uttids = []
bulk_spk_list = []
    
for root, dirnames, filenames in os.walk(data_dir,topdown=True):
    for filename in fnmatch.filter(sorted(filenames), "*.wav"):
        dirname = root.split("/")[-1]
        wavname = filename[:-4]
        
        utterance_id = wavname
        uttids.append(utterance_id)
        
        spk = wavname[0:9]
        bulk_spk_list.append(spk) if spk not in bulk_spk_list else bulk_spk_list
        


# Split the utterances into 80% train, 10% dev and 10% test
# Make sure to always shuffle with a fixed seed so that the split is reproducible
random.seed(230)
uttids.sort() 
random.shuffle(uttids)

split1 = int(0.8 * len(uttids))
split2 = int(0.1 * len(uttids))
train_uttids = uttids[:split1]
dev_uttids = uttids[split1 : (split1 + split2)]
test_uttids = uttids[(split1 + split2):]

     
nf = open(uttid_dir + '/'+ 'train.uttids', 'w')
nf.write('\n'.join(train_uttids))
nf.close()

nf = open(uttid_dir + '/'+ 'dev.uttids', 'w')
nf.write('\n'.join(dev_uttids))
nf.close()

nf = open(uttid_dir + '/'+ 'test.uttids', 'w')
nf.write('\n'.join(dev_uttids))
nf.close()

print("Data generation")

#remove punctutions and numbers
table = str.maketrans(dict.fromkeys(string.punctuation+'‘’0123456789Ielnrtx' + '\u200c' + '\u200d'))

text_male_dict = {}
with open(data_dir + 'line_index_male.tsv','r') as f:
    text_male = f.read().split('\n')

for row in text_male:
    utt_id = row[:21] 
    a = row[22:]
    a_new = a.translate(table)
    text_male_dict[utt_id] = a_new
    
text_female_dict = {}
with open(data_dir + 'line_index_female.tsv','r') as f:
    text_female = f.read().split('\n')

for row in text_female:
    utt_id = row[:21] 
    a = row[22:]
    a_new = a.translate(table)
    text_female_dict[utt_id] = a_new

for x in ["train", "dev", "test"]: 
    ref_file = open(uttid_dir + x +'.uttids','r')
    ref_file_content = ref_file.read().split('\n')
    
    utt2spk_list = []
    spk_list = []
    text_list = []
    wav_list = []
    spk2gender_list = []
    for item in ref_file_content:
        spk = item[:9]                  # speaker info
        spk_list.append(spk)
        
        # utt2spk  : uttid spk
        utt2spk_str = item + ' ' + spk     # utterance_id + speaker
        utt2spk_list.append(utt2spk_str)
        
        if spk.split('_')[0] == 'knm':
            # wav.scp : uttid wav_location
            file_path = data_dir + 'male' + '/' + item +'.wav'
            wav_str = item + ' ' + 'sox ' + file_path + ' -t wav -r 16000 -b 16 - |'
            wav_list.append(wav_str)
            
            # # spk2gender 
            gender = 'm' 
            spk2gender_str = spk +' '+ gender
            spk2gender_list.append(spk2gender_str)
            
            # text file  : uttid transcript
            text_str = item + ' ' + text_male_dict[item]   
            text_list.append(text_str)
        else:
            # wav.scp : uttid wav_location
            file_path = data_dir + 'female' + '/' + item +'.wav'
            wav_str = item + ' ' + 'sox ' + file_path + ' -t wav -r 16000 -b 16 - |'
            wav_list.append(wav_str)
            
            # # spk2gender 
            gender = 'f' 
            spk2gender_str = spk +' '+ gender
            spk2gender_list.append(spk2gender_str)
            
            # text file  : uttid transcript
            text_str = item + ' ' + text_female_dict[item]   
            text_list.append(text_str)
    
    #sorting
    utt2spk_list.sort()
    wav_list.sort()
    spk2gender_list = list(set(spk2gender_list))
    spk2gender_list.sort()
    text_list.sort()
    spk_list = list(set(spk_list))
    spk_list.sort()
     
    utt2spk_file = open(uttid_dir + x + '.utt2spk','w')
    for item in utt2spk_list:
        utt2spk_file.write(item+'\n')
    utt2spk_file.close()
        
    wav_file = open(uttid_dir + x +'_wav.scp','w')
    for item in wav_list:
        wav_file.write(item+'\n')
    wav_file.close()
    
    spk2gender_file = open(uttid_dir + x + '.spk2gender','w')
    for item in spk2gender_list:
        spk2gender_file.write(item+'\n')
    spk2gender_file.close()
    
    text_file = open(uttid_dir + x + '.text','w')
    for item in text_list:
        text_file.write(item+'\n')
    text_file.close()
    
    ref_file = open(uttid_dir + x +'.utt2spk','r')
    ref_file_content = ref_file.read().split('\n')
    ref_file_content.remove('')
    
    spk2utt_dict = {}
    for spk in spk_list:
        spk2utt_dict[spk] = []     
         
    for item in ref_file_content:
        spk = item.split(' ')[1]
        spk2utt_dict[spk].append(item.split(' ')[0])

    file = open(uttid_dir + x + '.spk2utt','w')
    for spk in spk_list:
        utt_list = spk2utt_dict[spk]
    
        #spk2utt_str = spk + ' ' + ' '.join([str(elem) for elem in utt_list])
        spk2utt_str = spk
        for utt in utt_list:
            spk2utt_str = spk2utt_str + ' ' + utt
        spk2utt_str = spk2utt_str + '\n'
        file.write(spk2utt_str)

    file.close()