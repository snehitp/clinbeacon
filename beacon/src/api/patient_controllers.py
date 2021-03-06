"""
@package api
Beacon Management API Controllers
"""
from flask import Blueprint, jsonify, request, flash
from api import log
from lib.beacondb import VcfSampleCollection, IndividualCollection, VcfFileCollection
from api.auth import requires_auth
from werkzeug.utils import secure_filename
import vcf
import io
import re

patient_controllers = Blueprint('patient_controllers', __name__)

@patient_controllers.route('', methods = ['GET'])
@requires_auth
def get_patient_list():
    """ Retrieve a list of patients """

    list = IndividualCollection().get_all();

    return jsonify(list)

@patient_controllers.route('', methods = ['POST'])
@requires_auth
def create_patient():
    """ Create a new patient """

    document = request.json
    
    return jsonify({'id':IndividualCollection().add(document)})

@patient_controllers.route('/<id>', methods = ['GET'])
@requires_auth
def get_patient(id):
    """ Get a specific patient by id """
    return jsonify(IndividualCollection().get_by_id(id))

@patient_controllers.route('/<id>', methods = ['DELETE'])
@requires_auth
def delete_patient(id):
    """ Delete a patient """
    
    IndividualCollection().delete(id)

    return jsonify({'result':'ok'})

@patient_controllers.route('/<id>/sample/<sampleId>', methods = ['GET'])
@requires_auth
def get_patient_sample(id, sampleId):
    """ Delete a VCF sample """

    return jsonify({'result':'ok'})

@patient_controllers.route('/<id>/sample/<sampleId>', methods = ['DELETE'])
@requires_auth
def delete_patient_samples(id, sampleId):
    """ Delete a VCF sample """

    return jsonify({'result':'ok'})

@patient_controllers.route('/<id>/sample', methods = ['GET'])
@requires_auth
def get_patient_samples(id):
    """ Get all gene samples for an individual """
    list = VcfSampleCollection().get_by_individualid(id)

    # add query string to fetch (status and filter by ids)

    return jsonify(list)

@patient_controllers.route('/<id>/sample', methods = ['POST'])
@requires_auth
def upload_patient_samples(id):
    """
    VCF file upload operation
    """

    try:
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error':'no file in file part'})

        log.info('request files - %s', request.files)

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            log.error('patient upload file name is empty')
            flash('No selected file')
            return jsonify({'error':'no file'})

        # 1) VALIDATE FILE AND WRITE HEADER RECORD
        # 2) SAVE FILE TO VCF STORAGE PATH
        # 3) QUEUE IMPORT PROCESSING

        # this is used to ensure we can safely use the filename sent to us
        #filename = secure_filename(file.filename)

        # load data from the stream into memory for processing
        data = file.read()
        stream = io.StringIO(data.decode('utf-8'))
        vcf_reader = vcf.Reader(stream)

        # This approach creates a document for each sample
        samples = next(vcf_reader).samples
        sample_count = len(samples)
        
        stream.seek(0)
        vcf_reader = vcf.Reader(stream)

        for i in range(0, sample_count):
            stream.seek(0)
            vcf_reader = vcf.Reader(stream)
            variants = list()

            for record in vcf_reader:
                sample = record.samples[i]

                #TODO - there are better ways to handle this
                    # Do we need to store the reference for this query
                # sample = record.samples[0]
                alleles = []
                if sample.gt_bases is not None:
                    log.info(sample.gt_bases)
                    alleles = re.split(r'[\\/|]', sample.gt_bases)
                    # remove duplicates
                    alleles = set(alleles)

                for allele in alleles:
                    chrom = record.CHROM
                    # remove preceeding chr if exists
                    if (re.match('chr', chrom, re.I)):
                        chrom = chrom[3:]
                    if chrom in ['1', '2', '3', '4', '5', '6', '7', '8', '9','10','11','12','13','14','15','16','17','18','19','20','21','22', 'X', 'Y', 'M' ]:
                        variants.append(chrom + '_' + str(record.POS) + '_' + allele)

            # insert samples into the database
            VcfSampleCollection().add(
                {
                    'patientId': id,
                    'variants': variants}
                )
    except:
        log.exception('error importing patient vcf')
    
    # TODO: change this to return import stats
    return jsonify({'result':'ok'})
