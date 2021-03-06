import glob
import inspect
import time
import warnings
from os import path
from pathlib import Path
from typing import Union

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import image, masking, _utils
from nilearn.input_data import NiftiMasker
from sklearn.base import BaseEstimator

from photonai.photonlogger.logger import logger

from photonai_neuro.objects import MaskObject, AtlasObject, RoiObject, NiftiConverter


class AtlasLibrary:
    ATLAS_DICTIONARY = {'AAL': 'AAL.nii.gz',
                        'HarvardOxford_Cortical_Threshold_25': 'HarvardOxford-cort-maxprob-thr25.nii.gz',
                        'HarvardOxford_Subcortical_Threshold_25': 'HarvardOxford-sub-maxprob-thr25.nii.gz',
                        'HarvardOxford_Cortical_Threshold_50': 'HarvardOxford-cort-maxprob-thr50.nii.gz',
                        'HarvardOxford_Subcortical_Threshold_50': 'HarvardOxford-sub-maxprob-thr50.nii.gz',
                        'Yeo_7': 'Yeo2011_7Networks_MNI152_FreeSurferConformed1mm.nii.gz',
                        'Yeo_7_Liberal': 'Yeo2011_7Networks_MNI152_FreeSurferConformed1mm_LiberalMask.nii.gz',
                        'Yeo_17': 'Yeo2011_17Networks_MNI152_FreeSurferConformed1mm.nii.gz',
                        'Yeo_17_Liberal': 'Yeo2011_17Networks_MNI152_FreeSurferConformed1mm_LiberalMask.nii.gz',
                        'Schaefer2018_100Parcels_7Networks': 'Schaefer2018_100Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_200Parcels_7Networks': 'Schaefer2018_200Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_300Parcels_7Networks': 'Schaefer2018_300Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_400Parcels_7Networks': 'Schaefer2018_400Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_500Parcels_7Networks': 'Schaefer2018_500Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_600Parcels_7Networks': 'Schaefer2018_600Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_700Parcels_7Networks': 'Schaefer2018_700Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_800Parcels_7Networks': 'Schaefer2018_800Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_900Parcels_7Networks': 'Schaefer2018_900Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_1000Parcels_7Networks': 'Schaefer2018_1000Parcels_7Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_100Parcels_17Networks': 'Schaefer2018_100Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_200Parcels_17Networks': 'Schaefer2018_200Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_300Parcels_17Networks': 'Schaefer2018_300Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_400Parcels_17Networks': 'Schaefer2018_400Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_500Parcels_17Networks': 'Schaefer2018_500Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_600Parcels_17Networks': 'Schaefer2018_600Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_700Parcels_17Networks': 'Schaefer2018_700Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_800Parcels_17Networks': 'Schaefer2018_800Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_900Parcels_17Networks': 'Schaefer2018_900Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',
                        'Schaefer2018_1000Parcels_17Networks': 'Schaefer2018_1000Parcels_17Networks_order_FSLMNI152_1mm.nii.gz',}

    MASK_DICTIONARY = {'MNI_ICBM152_GrayMatter': 'mni_icbm152_gm_tal_nlin_sym_09a.nii.gz',
                       'MNI_ICBM152_WhiteMatter': 'mni_icbm152_wm_tal_nlin_sym_09a.nii.gz',
                       'MNI_ICBM152_WholeBrain': 'mni_icbm152_t1_tal_nlin_sym_09a_mask.nii.gz',
                       'Cerebellum': 'P_08_Cere.nii.gz'}

    LIBRARY = dict()

    def __init__(self):
        self.photon_atlases = self._load_photon_atlases()
        self.photon_masks = self._load_photon_masks()

    def _load_photon_atlases(self):
        """
        Intern function for creating AtlasObjects for every available Atlas in the ATLAS_DICTIONARY.
        :return: photon_atlases: dict, dict atlas by atlas_id
        """
        dir_atlases = path.join(path.dirname(inspect.getfile(BrainAtlas)), 'atlases')
        photon_atlases = dict()
        for atlas_id, atlas_info in self.ATLAS_DICTIONARY.items():
            atlas_file = glob.glob(path.join(dir_atlases, path.join('*', atlas_info)))[0]
            atlas_basename = path.basename(atlas_file)[:-7]
            atlas_dir = path.dirname(atlas_file)
            photon_atlases[atlas_id] = AtlasObject(name=atlas_id, path=atlas_file,
                                                   labels_file=path.join(atlas_dir, atlas_basename + '_labels.txt'))
        return photon_atlases

    def _load_photon_masks(self):
        """
        Intern function for creating MaskObjects for every available Mask in the MASK_DICTIONARY.
        :return: photon_masks: dict, Mask by mask_id
        """
        dir_atlases = path.join(path.dirname(inspect.getfile(BrainAtlas)), 'atlases')
        photon_masks = dict()
        for mask_id, mask_info in self.MASK_DICTIONARY.items():
            mask_file = glob.glob(path.join(dir_atlases, path.join('*', mask_info)))[0]
            photon_masks[mask_id] = MaskObject(name=mask_id, mask_file=mask_file)
        return photon_masks

    def list_rois(self, atlas: str):
        """
        ROI listing of specific atlas
        :param atlas: str, atlas name
        :return: roi_names: list, list of ROIs
        """
        if atlas not in self.ATLAS_DICTIONARY.keys():
            msg = 'Atlas {} is not supported.'.format(atlas)
            logger.warning(msg)
            warnings.warn(msg)
            roi_names = []
        else:
            atlas = self.get_atlas(atlas)
            roi_names = [roi.label for roi in atlas.roi_list]
        return roi_names

    def _add_atlas_to_library(self, atlas_name:str, target_affine=None, target_shape=None, mask_threshold=None):
        """
        Loading Atlas into the Library by name.
        :param atlas_name:
        :param target_affine:
        :param target_shape:
        :param mask_threshold:
        :return:

        Todo: find solution for multiprocessing spaming
        """
        # load atlas object from photon_atlasses
        if atlas_name in self.photon_atlases.keys():
            original_atlas_object = self.photon_atlases[atlas_name]
        else:
            logger.debug("Checking custom atlas")
            original_atlas_object = self._check_custom_atlas(atlas_name)

        # now create new atlas object with different affine, shape and mask_threshold
        atlas_object = AtlasObject(name=original_atlas_object.name,
                                   path=original_atlas_object.path,
                                   labels_file=original_atlas_object.labels_file,
                                   mask_threshold=mask_threshold,
                                   affine=target_affine,
                                   shape=target_shape)

        # load atlas
        img = image.load_img(atlas_object.path)
        resampled_img = self._resample(img, target_affine=target_affine, target_shape=target_shape)
        atlas_object.atlas = resampled_img
        atlas_object.map = np.asarray(atlas_object.atlas.get_fdata())

        # apply mask threshold
        if mask_threshold is not None:
            atlas_object.map[atlas_object.map < mask_threshold] = 0
            atlas_object.map = atlas_object.map.astype(int)

        # now get indices
        atlas_object.indices = list(np.unique(atlas_object.map))

        # check labels
        if Path(atlas_object.labels_file).is_file():  # if we have a file with indices and labels
            labels = pd.read_table(atlas_object.labels_file, header=None)
            labels_dict = pd.Series(labels.iloc[:, 1].values, index=labels.iloc[:, 0]).to_dict()

            # check if background has been defined in labels.txt
            if 0 not in labels_dict.keys() and 0 in atlas_object.indices:
                # add 0 as background
                labels_dict[0] = 'Background'

            # check if map indices correspond with indices in the labels file
            if not sorted(atlas_object.indices) == sorted(list(labels_dict.keys())):
                logger.error("""
                The indices in map image ARE NOT the same as those in your *_labels.txt! Ignoring *_labels.txt.
                MapImage: 
                {}
                File: 
                {}
                """.format(str(sorted(self.indices)), str(sorted(list(labels_dict.keys())))))

                atlas_object.roi_list = [RoiObject(index=i, label=str(i), size=np.sum(i == atlas_object.map)) for i in
                                         atlas_object.indices]
            else:
                for i in range(len(atlas_object.indices)):
                    roi_index = atlas_object.indices[i]
                    new_roi = RoiObject(index=roi_index, label=labels_dict[roi_index].replace('\n', ''),
                                        size=np.sum(roi_index == atlas_object.map))
                    atlas_object.roi_list.append(new_roi)

        else:  # if we don't have a labels file, we just use str(indices) as labels
            atlas_object.roi_list = [RoiObject(index=i, label=str(i), size=np.sum(i == atlas_object.map)) for i in
                                     atlas_object.indices]

        # check for empty ROIs and create roi mask
        for roi in atlas_object.roi_list:

            if roi.size == 0:
                continue

            roi.mask = image.new_img_like(atlas_object.path, atlas_object.map == roi.index)

            # check if roi is empty
            if np.sum(roi.mask.dataobj != 0) == 0:
                roi.is_empty = True

        # finally add atlas to atlas library
        AtlasLibrary.LIBRARY[(atlas_name, str(target_affine), str(target_shape), str(mask_threshold))] = atlas_object
        logger.debug("BrainAtlas: Done adding atlas to library!")

    def _add_mask_to_library(self, mask_name: str = '', target_affine=None, target_shape=None, mask_threshold=0.5):
        # Todo: find solution for multiprocessing spaming

        if mask_name in self.photon_masks.keys():
            original_mask_object = self.photon_masks[mask_name]
        else:
            logger.debug("Checking custom mask")
            original_mask_object = self._check_custom_mask(mask_name)

        mask_object = MaskObject(name=mask_name, mask_file=original_mask_object.mask_file)

        #mask_object.mask = image.threshold_img(mask_object.mask_file, threshold=mask_threshold)
        mask_object.mask = image.math_img('img > {}'.format(mask_threshold), img=mask_object.mask_file)

        if target_affine is not None and target_shape is not None:
            mask_object.mask = self._resample(mask_object.mask, target_affine=target_affine, target_shape=target_shape)

        # check if roi is empty
        if np.sum(mask_object.mask.dataobj != 0) == 0:
            mask_object.is_empty = True
            msg = 'No voxels in mask after resampling (' + mask_object.name + ').'
            logger.error(msg)
            raise ValueError(msg)

        AtlasLibrary.LIBRARY[(mask_object.name, str(target_affine), str(target_shape), str(mask_threshold))] = mask_object
        logger.debug("BrainMask: Done adding mask to library!")

    def get_atlas(self, atlas_name, target_affine=None, target_shape=None, mask_threshold=None):
        if (atlas_name, str(target_affine), str(target_shape), str(mask_threshold)) not in AtlasLibrary.LIBRARY:
            self._add_atlas_to_library(atlas_name, target_affine, target_shape, mask_threshold)

        return AtlasLibrary.LIBRARY[(atlas_name, str(target_affine), str(target_shape), str(mask_threshold))]

    def get_mask(self, mask_name, target_affine=None, target_shape=None, mask_threshold=0.5):
        if (mask_name, str(target_affine), str(target_shape)) not in AtlasLibrary.LIBRARY:
            self._add_mask_to_library(mask_name, target_affine, target_shape, mask_threshold)

        return AtlasLibrary.LIBRARY[(mask_name, str(target_affine), str(target_shape), str(mask_threshold))]

    @staticmethod
    def _resample(mask, target_affine, target_shape):
        if target_affine is not None and target_shape is not None:
            mask = image.resample_img(mask, target_affine=target_affine, target_shape=target_shape, interpolation='nearest')
            # check orientations
            orient_data = ''.join(nib.aff2axcodes(target_affine))
            orient_roi = ''.join(nib.aff2axcodes(mask.affine))
            if not orient_roi == orient_data:
                msg = 'Orientation of mask and data are not the same: ' + \
                      orient_roi + ' (mask) vs. ' + orient_data + ' (data)'
                logger.error(msg)
                raise ValueError(msg)
        return mask

    @staticmethod
    def _check_custom_mask(mask_file):
        if not path.isfile(mask_file):
            msg = "Cannot find custom mask {}".format(mask_file)
            logger.error(msg)
            raise FileNotFoundError(msg)
        return MaskObject(name=mask_file, mask_file=mask_file)

    @staticmethod
    def _check_custom_atlas(atlas_file):
        if not path.isfile(atlas_file):
            msg = "Cannot find custom atlas {}".format(atlas_file)
            logger.error(msg)
            raise FileNotFoundError(msg)
        labels_file = path.split(atlas_file)[0] + '_labels.txt'
        if not path.isfile(labels_file):
            msg = "Didn't find .txt file with ROI labels. Using indices as labels."
            logger.warning(msg)
            warnings.warn(msg)
        return AtlasObject(name=atlas_file, path=atlas_file, labels_file=labels_file)

    @staticmethod
    def find_rois_by_label(atlas_obj: AtlasObject, query_list: list):
        """
        Returns all ROIs of given AtlasObject with roi_label in query_list.
        :param atlas_obj: AtlasObject, the object we are searching in
        :param query_list: serach after the ROI labels
        :return:
        """
        return [i for i in atlas_obj.roi_list if i.label in query_list]

    @staticmethod
    def find_rois_by_index(atlas_obj: AtlasObject, query_list: list):
        """
        Returns all ROIs of given AtlasObject with roi_index in query_list.
        :param atlas_obj: AtlasObject, the object we are searching in
        :param query_list: serach after the ROI index
        :return:
        """
        return [i for i in atlas_obj.roi_list if i.index in query_list]

    @staticmethod
    def get_nii_files_from_folder(folder_path: str, extension: str=".nii.gz"):
        """
        Returns all file with given extension in folder path.
        :param folder_path: str, path to folder
        :param extension: str, file extension
        :return: _: list
        """
        return glob.glob(folder_path + '*' + extension)


class BrainAtlas(BaseEstimator):
    """
    BrainAtlas is a transformer calculate brain atlases from input niftis.

    Parameter
    ---------
    * `atlas_name`: [str]:
        Name of specific Atlas. Possible values can be looked up in AtlasLibrary.
    * `extract_mode`: [str] - [default: 'vec']:
        The mode performing on ROI. Possible values: ['vec', 'mean', 'box', 'img']
    * `mask_threshold`: [str]:
        Mask Threshold. value < mask_threshold => value = 0
    * `background_id`: [str]:
        The background ID for ROI.

    # ToDo
        #   + check RAS vs. LPS view-type and provide warning
        #  - unit tests
        #  Later
        #  - add support for overlapping ROIs and probabilistic atlases using 4d-nii
        #  - add support for 4d resting-state data using nilearn
    """
    def __init__(self,
                 atlas_name: str,
                 extract_mode: str = 'vec',
                 mask_threshold: float = None,
                 background_id: int = 0,
                 rois: Union[list, str] = 'all'):


        self.atlas_name = atlas_name
        self.extract_mode = extract_mode
        # collection mode default to concat --> can only be overwritten by AtlasMapper
        self.collection_mode = 'concat'
        self.mask_threshold = mask_threshold
        self.background_id = background_id
        self.rois = rois
        self.box_shape = []
        self.is_transformer = True
        self.mask_indices = None
        self.affine = None
        self.shape = None
        self.needs_y = False
        self.needs_covariates = False
        self.roi_allocation = {}

    def fit(self, X, y):
        return self

    def transform(self, X, y=None, **kwargs):
        """

        :param X: input data
        :param y: targets
        :param kwargs:
        :return: roi_data: np.ndarray, ROIs data for given brain atlas in concat or list form.
        """

        X, n_subjects = NiftiConverter.transform(X)

        if self.collection_mode == 'list' or self.collection_mode == 'concat':
            collection_mode = self.collection_mode
        else:
            msg = "Collection mode {} not supported. Use 'list' or 'concat' instead." +\
                           "Falling back to concat mode.".format(self.collection_mode)
            logger.error(msg)
            raise ValueError(msg)

        # 1. validate if all X are in the same space and have the same voxelsize and have the same orientation

        # get ROI mask
        self.affine, self.shape = BrainMask.get_format_info_from_first_image(X)
        atlas_obj = AtlasLibrary().get_atlas(self.atlas_name, self.affine, self.shape, self.mask_threshold)
        roi_objects = self._get_rois(atlas_obj, which_rois=self.rois, background_id=self.background_id)

        roi_data = [list() for i in range(n_subjects)]
        roi_data_concat = list()
        t1 = time.time()

        # convert to series and C ordering since this will speed up the masking process
        series = _utils.as_ndarray(_utils.niimg._safe_get_data(X), dtype='float32', order="C", copy=True)
        mask_indices = list()

        # calculate roi_data for every ROI object by looping
        for i, roi in enumerate(roi_objects):
            self.roi_allocation[roi.label] = i

            logger.debug("Extracting ROI {}".format(roi.label))
            # simply call apply_mask to extract one roi
            extraction = self.apply_mask(series, roi.mask)
            if collection_mode == 'list':
                for sub_i in range(extraction.shape[0]):
                    roi_data[sub_i].append(extraction[sub_i])
                mask_indices.append(i)
            else:
                roi_data_concat.append(extraction)
                mask_indices.append(np.ones(extraction[0].size) * i)

        if self.collection_mode == 'concat':
            if n_subjects > 1:
                roi_data = np.concatenate(roi_data_concat, axis=1)
                self.mask_indices = np.concatenate(mask_indices)
            else:
                roi_data = np.array(roi_data_concat)
                self.mask_indices = mask_indices
        else:
            self.mask_indices = mask_indices

        elapsed_time = time.time() - t1
        logger.debug("Time for extracting {} ROIs in {} subjects: {} seconds".format(len(roi_objects),
                                                                                     n_subjects, elapsed_time))
        return roi_data

    def apply_mask(self, series, mask_img):
        """
        Apply mask on series.
        :param series: np.ndarray, data working on
        :param mask_img:
        :return:
        """
        mask_img = _utils.check_niimg_3d(mask_img)
        mask, mask_affine = masking._load_mask_img(mask_img)
        mask_img = image.new_img_like(mask_img, mask, mask_affine)
        mask_data = _utils.as_ndarray(mask_img.get_fdata(),
                                      dtype=np.bool)
        return series[mask_data].T

    def inverse_transform(self, X, y=None, **kwargs):
        """
        Reconstruct image from transformed data.
        :param X: data
        :param y: targets
        :param kwargs:
        :return:
        """
        X = np.asarray(X)

        # get ROI masks
        atlas_obj = AtlasLibrary().get_atlas(self.atlas_name, self.affine, self.shape, self.mask_threshold)
        roi_objects = self._get_rois(atlas_obj, which_rois=self.rois, background_id=self.background_id)

        unmasked = np.squeeze(np.zeros_like(atlas_obj.map, dtype='float32'))

        for i, roi in enumerate(roi_objects):
            mask, mask_affine = masking._load_mask_img(roi.mask)
            mask_img = image.new_img_like(roi.mask, mask, mask_affine)
            mask_data = _utils.as_ndarray(mask_img.get_fdata(), dtype=np.bool)

            if self.collection_mode == 'list':
                unmasked[mask_data] = X[i]
            else:
                unmasked[mask_data] = X[self.mask_indices == i]

        new_image = image.new_img_like(atlas_obj.atlas, unmasked)
        return new_image

    def _validity_check_roi_extraction(self, X, y=None, filename='validity_check.nii', **kwargs):
        new_image = self.inverse_transform(X, y, **kwargs)
        new_image.to_filename(filename)

    @staticmethod
    def _get_rois(atlas_obj, which_rois='all', background_id=0):

        if isinstance(which_rois, str):
            if which_rois == 'all':
                return [roi for roi in atlas_obj.roi_list if roi.index != background_id]
            else:
                return AtlasLibrary().find_rois_by_label(atlas_obj, [which_rois])

        elif isinstance(which_rois, int):
            return AtlasLibrary().find_rois_by_index(atlas_obj, [which_rois])

        elif isinstance(which_rois, list):
            if isinstance(which_rois[0], str):
                if which_rois[0].lower() == 'all':
                    return [roi for roi in atlas_obj.roi_list if roi.index != background_id]
                else:
                    return AtlasLibrary().find_rois_by_label(atlas_obj, which_rois)
            else:
                return AtlasLibrary().find_rois_by_index(atlas_obj, which_rois)


class BrainMask(BaseEstimator):

    def __init__(self, mask_image='MNI_ICBM152_WholeBrain', affine=None, shape=None, mask_threshold=0.5, extract_mode='vec'):
        self.mask_image = mask_image
        self.affine = affine
        self.shape = shape
        self.masker = None
        self.extract_mode = extract_mode
        self.mask_threshold = mask_threshold

    @staticmethod
    def get_format_info_from_first_image(X):

        img, n_subjects = NiftiConverter.transform(X)
        if n_subjects > 1:
            img = img.slicer[:, :, :, 0]

        if img is not None:
            if len(img.shape) > 3:
                img_shape = img.shape[:3]
            else:
                img_shape = img.shape
            return img.affine, img_shape
        else:
            msg = "Could not load image for affine and shape definition."
            logger.error(msg)
            raise ValueError(msg)

    @staticmethod
    def _get_box(in_imgs, roi):
        # get ROI infos
        map = roi.mask.get_fdata()
        true_points = np.argwhere(map)
        corner1 = true_points.min(axis=0)
        corner2 = true_points.max(axis=0)
        box = []
        for img in in_imgs:
            if isinstance(img, str):
                data = image.load_img(img).get_fdata()
            else:
                data = img.get_fdata()
            tmp = data[corner1[0]:corner2[0] + 1, corner1[1]:corner2[1] + 1, corner1[2]:corner2[2] + 1]
            box.append(tmp)
        return np.asarray(box)

    def fit(self, X, y):
        return self

    def transform(self, X, y=None, **kwargs):

        if self.affine is None or self.shape is None:
            self.affine, self.shape = BrainMask.get_format_info_from_first_image(X)

        if isinstance(self.mask_image, str):
            self.mask_image = AtlasLibrary().get_mask(self.mask_image, self.affine, self.shape, self.mask_threshold)
        elif isinstance(self.mask_image, RoiObject):
            pass

        if not self.mask_image.is_empty:
            self.masker = NiftiMasker(mask_img=self.mask_image.mask, target_affine=self.affine,
                                      target_shape=self.shape, dtype='float32')
            try:
                single_roi = self.masker.fit_transform(X)
            except BaseException as e:
                logger.error(e)
                single_roi = None

            if single_roi is not None:
                if self.extract_mode == 'vec':
                    return np.asarray(single_roi)

                elif self.extract_mode == 'mean':
                    return np.mean(single_roi, axis=1)

                elif self.extract_mode == 'box':
                    return BrainMask._get_box(X, self.mask_image)

                elif self.extract_mode == 'img':
                    return self.masker.inverse_transform(single_roi)

                else:
                    msg = "Currently there are no other methods than 'vec', 'mean', 'img' and 'box' supported!"
                    logger.error(msg)
                    raise NameError(msg)
            else:
                if isinstance(X, str):
                    msg = "Extracting ROI failed for " + X
                elif isinstance(X, list) and isinstance(X[0], str):
                    msg = "Extracting ROI failed for item in" + str(X)
                else:
                    msg = "Extracting ROI failed for nifti image obj. Cannot trace back path of failed file."
                logger.error(msg)
                raise ValueError(msg)
        else:
            msg = "Skipping self.mask_image " + self.mask_image.label + " because it is empty."
            logger.error(msg)
            raise ValueError(msg)

    def inverse_transform(self, X, y=None, **kwargs):
        if not self.extract_mode == 'vec':
            msg = "BrainMask extract_mode={} is not supported with inverse_transform".format(self.extract_mode)
            logger.error(msg)
            raise NotImplementedError(msg)

        return self.masker.inverse_transform(X)
