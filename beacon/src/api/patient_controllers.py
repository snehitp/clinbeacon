"""
@package api
Beacon Management API Controllers
"""
from flask import Blueprint, jsonify, request
from api.database import DataAccess
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

    list = DataAccess().get_patients();

    return jsonify(list)

@patient_controllers.route('', methods = ['POST'])
@requires_auth
def create_patient():
    """ Create a new patient """

    document = request.json
    
    return jsonify({'id':DataAccess().add_patient(document)})

@patient_controllers.route('/<id>', methods = ['GET'])
@requires_auth
def get_patient(id):
    """ Get a specific patient by id """

    return jsonify({'result':'ok'})

@patient_controllers.route('/<id>', methods = ['DELETE'])
@requires_auth
def delete_patient(id):
    """ Delete a patient """
    
    DataAccess().delete_patient(id)

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
    """ Get a VCF sample """
    list = DataAccess().get_patient_samples(id)

    return jsonify(list)

@patient_controllers.route('/<id>/sample', methods = ['POST'])
@requires_auth
def import_patient_samples(id):
    """
    VCF file upload operation
    """
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error':'no file in file part'})

    print(request.files)

    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return jsonify({'error':'no file'})

    # this is used to ensure we can safely use the filename sent to us
    #filename = secure_filename(file.filename)

    # load data from the stream into memory for processing
    data = file.read()
    vcf_reader = vcf.Reader(io.StringIO(data.decode('utf-8')))

    variants = list()
    for record in vcf_reader:
        
        #TODO process multiple samples in a vcf file
        sample = record.samples[0]

        #TODO - there are better ways to handle this
            # Do we need to store the reference for this query
        allleles = []
        if sample.gt_bases is not None:
            alleles = re.split(r'[\\/|]', sample.gt_bases)
            # remove duplicates
            alleles = set(alleles)

        for allele in alleles:
            chrom = record.CHROM
            # remove preceeding chr if exists
            if (re.match('chr', chrom, re.I)):
                chrom = chrom[3:]
            variants.append(chrom + '_' + str(record.POS) + '_' + allele)

    # insert samples into the database
    DataAccess().import_vcf(
        {
            'patientId': id,
            'variants': variants}
        )

    # TODO: change this to return stats
    return jsonify({'result':'ok'})