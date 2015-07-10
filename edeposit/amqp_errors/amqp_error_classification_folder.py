from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob

from edeposit.amqp_errors import MessageFactory as _

# Interface class; used to define content-type schema.

class IAMQPErrorClassificationFolder(form.Schema, IImageScaleTraversable):
    """
    Description of the Example Type
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/amqp_error_classification_folder.xml to define the content type.

    form.model("models/amqp_error_classification_folder.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

from operator import __eq__, itemgetter

class AMQPErrorClassificationFolder(Container):
    grok.implements(IAMQPErrorClassificationFolder)

    def getTrainData(self):
        items = filter(lambda pp: pp[1].portal_type == 'edeposit.amqp_errors.amqperrorclassification', self.items())
        trainData = map(lambda item: (item.errorText, item.errorType), map(itemgetter(1), items))
        return trainData

    def classifierFactory(self, trainData):
        return NaiveBayesClassifier(trainData)

    def updateClassificator(self):
        self.classificator = self.classifierFactory(self.getTrainData())

    def classifyError(errorText):
        if not getattr(self,'classifier',None):
            self.classifier = self.classifierFactory(self.getTrainData)

        prob_cl = self.classifier(errorText)
        result = prob_cl.max()
        return (result, prob_cl.prob(result))


    # Add your class methods and properties here
    pass


# View class
# The view will automatically use a similarly named template in
# amqp_error_classification_folder_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class TrainClassificatorView(grok.View):
    """ sample view class """

    grok.context(IAMQPErrorClassificationFolder)
    grok.require('zope2.View')
    grok.name('train-classificator')

    def classifiedRules(self):
        return self.getTrainedData()
